import abc

import numpy as np
import pandas as pd
from django.db import transaction
from django.db.models import Model

from sde import models


class Pipeline(abc.ABC):
    url: str = None
    model: Model = None

    def run(self):
        df = self.extract()
        df = self.transform(df=df)
        self.load(df=df)

    def extract(self) -> pd.DataFrame:
        df = pd.read_csv(self.url)
        return df

    @abc.abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    @transaction.atomic
    def load(self, df: pd.DataFrame):
        self.model.objects.all().delete()
        staged_records = []
        for _, row in df.iterrows():
            record = self.model(**row.to_dict())
            staged_records.append(record)
        self.model.objects.bulk_create(staged_records)


class CategoryPipeline(Pipeline):
    url = "https://www.fuzzwork.co.uk/dump/latest/invCategories.csv"
    model = models.Category

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            "id",
            "name",
            "icon",
            "published",
        ]
        df = df[df["published"] == True]  # noqa: E712
        columns = [
            "id",
            "name",
        ]
        df = df[columns]
        return df


class GroupPipeline(Pipeline):
    url = "https://www.fuzzwork.co.uk/dump/latest/invGroups.csv"
    model = models.Group

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            "id",
            "category_id",
            "name",
            "icon",
            "use_base_price",
            "anchored",
            "anchorable",
            "singleton",
            "published",
        ]
        df = df[df["published"] == True]  # noqa: E712
        columns = [
            "id",
            "name",
            "category_id",
        ]
        df = df[columns]
        return df


class MarketGroupPipeline(Pipeline):
    url = "https://www.fuzzwork.co.uk/dump/latest/invMarketGroups.csv"
    model = models.MarketGroup

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            "id",
            "parent_id",
            "name",
            "description",
            "icon",
            "has_types",
        ]
        columns = [
            "id",
            "name",
            "parent_id",
        ]
        df = df[columns]
        df = df.replace({np.nan: None})
        return df


class TypePipeline(Pipeline):
    url = "https://www.fuzzwork.co.uk/dump/latest/invTypes-nodescription.csv"
    model = models.Type

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            "id",
            "group_id",
            "name",
            "mass",
            "volume",
            "capacity",
            "portion-size",
            "race_id",
            "base_price",
            "published",
            "market_group_id",
            "icon_id",
            "sound_id",
            "graphic_id",
        ]
        columns = [
            "id",
            "group_id",
            "name",
            "volume",
            "published",
            "market_group_id",
        ]
        df = df[columns]
        df = df[df["published"] == True]  # noqa: E712
        df = df[df["market_group_id"] != "\\N"]
        columns = [
            "id",
            "group_id",
            "name",
            "volume",
            "market_group_id",
        ]
        df = df[columns]
        df = self._fix_volumes(df=df)
        return df

    def _fix_volumes(self, df: pd.DataFrame) -> pd.DataFrame:
        volumes_df = pd.read_csv("https://www.fuzzwork.co.uk/dump/latest/invVolumes.csv")
        volumes_df.columns = ["id", "volume"]

        # Join dfs on id, add volume_correct col, update volume, drop volume_correct col
        merged_df = df.merge(volumes_df, on="id", how="left", suffixes=("", "_correct"))
        merged_df["volume"] = merged_df["volume_correct"].where(
            pd.notnull(merged_df["volume_correct"]), merged_df["volume"]
        )
        merged_df = merged_df.drop(columns="volume_correct")
        df = merged_df
        return df


class MetaGroupPipeline(Pipeline):
    url = ""
    model = models.MetaGroup

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df


class MetaTypePipeline(Pipeline):
    url = ""
    model = models.MetaType

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df
