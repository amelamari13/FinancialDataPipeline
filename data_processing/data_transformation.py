from pyspark.sql import SparkSession
from pyspark.sql import Window
from pyspark.sql.functions import col, avg, round, when


def transform_data(df):
    # Créer une session Spark
    spark = SparkSession.builder \
        .appName("FinancialData") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .getOrCreate()

    # Convertir le DataFrame Pandas en DataFrame PySpark
    spark_df = spark.createDataFrame(df)
    spark_df.show(10)

    # Vérifier que les colonnes nécessaires existent
    required_columns = ["Open", "Close", "Date"]
    for column in required_columns:
        if column not in spark_df.columns:
            raise ValueError(f"Missing required column: {column}")

    # Calculer les rendements quotidiens
    spark_df = spark_df.withColumn(
        "Daily_Return",
        round((col("Close") - col("Open")) / col("Open") * 100, 2)
    )

    # Calculer la moyenne mobile sur 7 jours
    window_spec = Window.orderBy("Date").rowsBetween(-6, 0)  # moyenne mobile sur 7 jours
    spark_df = spark_df.withColumn(
        "7_Day_Moving_Avg",
        round(avg(col("Close")).over(window_spec), 2)
    )

    # Filtrer les jours à forte volatilité (rendement > 2%)
    spark_df = spark_df.withColumn(
        "HighVolatility",
        when(col("Daily_Return") > 2, 1).otherwise(0)
    )

    # Vérifier si le prix de clôture est au-dessus de la moyenne mobile
    spark_df = spark_df.withColumn(
        "Above_Moving_Avg",
        when(col("Close") > col("7_Day_Moving_Avg"), 1).otherwise(0)
    )

    return spark_df


def filter_large_transactions(spark_df, threshold):
    return spark_df.filter(spark_df['Volume'] > threshold)
