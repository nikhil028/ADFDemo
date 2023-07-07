# Databricks notebook source
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType,StructField, StringType, ArrayType

# COMMAND ----------

spark.conf.set(
    "fs.azure.account.key.storagedemo072023.dfs.core.windows.net", "7Q1EpHXMfumFAt7IEa8mwErS/Cu2wOFDSRbU4l4W0BuBLsm28QCo511+u9W2PL5FCZZm9KiDYpHI+ASt+uJqRQ==")

# COMMAND ----------

#spark.read.load("abfss://<container-name>@<storage-account-name>.dfs.core.windows.net/<path-to-data>")
dbutils.fs.ls("abfss://adfdemo@storagedemo072023.dfs.core.windows.net/")

# COMMAND ----------

def read_json(path):
    sch=StructType([
        StructField("id",StringType(),False),
        StructField("first_name",StringType(),True),
        StructField("last_name", StringType(), True),
        StructField("email",ArrayType(StringType()),True),
        StructField("address",StructType([
            StructField("state",StringType(),True),
            StructField("specific",StructType([
                StructField("city",StringType(),True),
                StructField("street",StringType(),True)]
            ))
        ]))
    ])
    df1 = spark.read.format('json').schema(sch).load(path)
    
    #Create separate columns for nested json
    df2 = df1.withColumn("name", concat_ws(" ","first_name","last_name"))\
        .withColumn("street",df1.address.specific["street"]).withColumn("city",df1.address.specific["city"])\
        .withColumn("state",df1.address["state"])\
        .drop("first_name","last_name","address","specific")
    
    df3 = df2.select("id","name","email","street","city","state")
    
    df3.show() 



# COMMAND ----------

def main():
    container = "abfss://adfdemo@storagedemo072023.dfs.core.windows.net/"
    file_path = dbutils.widgets.get("staginglocation")
    input_location = container+file_path
    read_json(input_location)


if __name__ == "__main__":
    main()
