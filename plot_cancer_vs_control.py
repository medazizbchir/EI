import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from lifelines.statistics import logrank_test
from lifelines import KaplanMeierFitter
from lifelines.plotting import add_at_risk_counts
import datetime
import altair as alt
import yaml
import os
from dateutil.relativedelta import relativedelta


kmf = KaplanMeierFitter()
kmf_c = KaplanMeierFitter()
# we assume that a patient who exit an hospital alife survives at least "survival_duration_days_if_survive" days
survival_duration_days_if_survive = 20


def get_df_kaplan(
    df_person_tmp,
    df_visit_tmp,
    # df_cond_tmp,
    df_med_tmp,
    t_end_of_study,
    age_range=None,
    gender=None,
    max_stay_duration=survival_duration_days_if_survive,
):
    df_visit_tmp = df_visit_tmp.query(
        "visit_start_datetime <= @t_end_of_study")
    # .merge(
    #     df_cond_tmp[["visit_occurrence_id"]], on="visit_occurrence_id", how="inner"
    # )

    # for each patient : duration, death ou not (then no info anymore)
    df_admin = (
        df_person_tmp.merge(df_visit_tmp, on="person_id", how="inner")
        .merge(
            df_med_tmp[["drug_source_value", "visit_occurrence_id"]],
            on="visit_occurrence_id",
            how="left",
        )
        .fillna({"drug_source_value": "control"})
    )

    # filtering
    if age_range is not None:
        df_admin = df_admin.assign(
            age=lambda pp: pp[["visit_start_datetime", "birth_datetime"]].apply(
                lambda r: relativedelta(
                    r["visit_start_datetime"], r["birth_datetime"]
                ).years,
                axis=1,
            )
        ).query(f"age<{age_range[1]} and age>={age_range[0]}")
    if gender is not None:
        df_admin = df_admin.query(f"gender_source_value=='{gender}'")

    # build df for kaplan-meier plot
    # 'T': durations
    # 'E': binary, representing whether the “death” was observed or not (alternatively an individual can be censored)

    # patients are dead if death_date is not null
    df_dead = df_admin.query("death_datetime == death_datetime").assign(
        T=lambda pp: (pp["death_datetime"] - pp["visit_start_datetime"]).apply(
            lambda x: int(x.days)
        ),
        E=lambda pp: 1,
    )

    # censored data: neither death_date nor visit_end_date
    df_not_finished = df_admin.query(
        "death_datetime != death_datetime and visit_end_datetime != visit_end_datetime"
    ).assign(
        T=lambda pp: (
            pd.to_datetime(t_end_of_study) - pp["visit_start_datetime"]
        ).apply(lambda x: int(x.days)),
        E=lambda pp: 0,
    )

    # fully observed livings: if no death_date but non null end_visit_date
    # reminder: we assume that a patient who exit an hospital alive survives at least "max_stay_duration" days
    df_alive = df_admin.query(
        "death_datetime != death_datetime and visit_end_datetime == visit_end_datetime"
    ).assign(
        T=lambda pp: max_stay_duration,
        E=lambda pp: 0,
    )

    # final concatenation
    df_kaplan = pd.concat([df_dead, df_not_finished, df_alive], axis=0)[
        ["T", "E", "drug_source_value"]
    ].rename(columns={"drug_source_value": "group"})
    df_kaplan["T"] = df_kaplan["T"].astype(int)
    return df_kaplan


def plot_primary_kaplan(
    df_person_kaplan,
    # df_cond_kaplan,
    list_case,
    t_end_of_study,
):
    fig, axs = plt.subplots(1, 2)
    fig.set_size_inches(10.5, 5.5)

    i = 0
    for df_visit_kaplan, df_med_kaplan, name in list_case:
        df_kaplan = get_df_kaplan(
            df_person_kaplan,
            df_visit_kaplan,
            # df_cond_kaplan,
            df_med_kaplan,
            t_end_of_study=t_end_of_study,
        )
        dfA = df_kaplan.query('group=="drugA"')
        dfB = df_kaplan.query('group=="drugB"')
        if i == 0:
            dfc = df_kaplan.query('group=="control"')
            kmf_c.fit(dfc["T"], dfc["E"], label="control")
            kmf_c.plot_survival_function(ax=axs[1])
            kmf_c.plot_survival_function(ax=axs[0])
        kmf.fit(dfA["T"], dfA["E"], label=f"drugA - {name}")
        kmf.plot_survival_function(ax=axs[0])
        add_at_risk_counts(kmf, kmf_c, ax=axs[0], rows_to_show=['At risk'])
        kmf.fit(dfB["T"], dfB["E"], label=f"drugB - {name}")
        kmf.plot_survival_function(ax=axs[1])
        add_at_risk_counts(kmf, kmf_c, ax=axs[1], rows_to_show=['At risk'])

        i += 1

    axs[0].set_title("drugA - all population")
    axs[1].set_title("drugB - all population")
    axs[0].set_ylim([0, 1.05])
    axs[1].set_ylim([0, 1.05])
    axs[0].xaxis.set_major_locator(MaxNLocator(integer=True))
    axs[1].xaxis.set_major_locator(MaxNLocator(integer=True))

    for ax in axs.flat:
        ax.set(xlabel="days after admission", ylabel="probability of survival")

    plt.tight_layout()
    plt.show()