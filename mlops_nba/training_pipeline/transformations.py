from sklearn import preprocessing


def prepare_for_model(df):
    df = df.drop(columns=["filename", "efficency", "Rk"], errors="ignore")
    le = preprocessing.LabelEncoder()
    for i in ["Player", "Pos", "Tm", "season", "data_period", "game_type"]:
        df.loc[:, i] = le.fit_transform(df.loc[:, i])
    return df
