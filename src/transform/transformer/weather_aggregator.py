import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from src.base.column_name import RentDataCN, WeatherDataCN, WeatherDataValue, TimeDataCN, TimeDataValue


class WeatherAggregator(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X: pd.DataFrame, y: pd.DataFrame = None):
        return self

    def transform(self, X: pd.DataFrame, y: pd.DataFrame = None):
        sampled_X = X[[
            RentDataCN.RENT_STATION,
            TimeDataCN.MONTH,
            TimeDataCN.DAY,
            TimeDataCN.HOUR,
            TimeDataCN.WEEKDAY,
            WeatherDataCN.PRECIPITATION,
            WeatherDataCN.SUNSHINE_DURATION
        ]].copy()
        return self.aggregate(sampled_X)

    # noinspection PyMethodMayBeStatic
    def aggregate(self, X: pd.DataFrame) -> pd.DataFrame:
        X[TimeDataCN.TIME_CATEGORY] = X[TimeDataCN.HOUR].apply(self.classify_time)
        X[RentDataCN.RENT_COUNT] = X.groupby([
            TimeDataCN.MONTH,
            TimeDataCN.DAY,
            TimeDataCN.TIME_CATEGORY,
            RentDataCN.RENT_STATION
        ])[RentDataCN.RENT_STATION].transform('count')

        X[WeatherDataCN.RAINFALL] = X.groupby([
            TimeDataCN.MONTH,
            TimeDataCN.DAY,
            TimeDataCN.TIME_CATEGORY,
            WeatherDataCN.PRECIPITATION
        ])[WeatherDataCN.PRECIPITATION].transform(
            lambda x: WeatherDataValue.RAIN if any(x > 0.5) else WeatherDataValue.NON_RAIN)

        X.drop_duplicates(subset=[
            TimeDataCN.MONTH,
            TimeDataCN.DAY,
            TimeDataCN.TIME_CATEGORY,
            RentDataCN.RENT_STATION
        ], inplace=True)

        X.drop([WeatherDataCN.PRECIPITATION], axis=1, inplace=True)

        return X

    # noinspection PyMethodMayBeStatic
    def classify_time(self, hour):
        if 7 <= hour <= 9:
            return TimeDataValue.MORNING_PEAK
        elif 10 <= hour <= 12:
            return TimeDataValue.MORNING_NON_PEAK
        elif 13 <= hour <= 16:
            return TimeDataValue.AFTERNOON_NON_PEAK
        elif 17 <= hour <= 19:
            return TimeDataValue.AFTERNOON_PEAK
        else:
            return TimeDataValue.NIGHTTIME
