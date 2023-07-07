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

def read_json(container,input_file_path):
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
    input_location = container+input_file_path
    df1 = spark.read.format('json').schema(sch).load(path)
    
    #Create separate columns for nested json
    df2 = df1.withColumn("name", concat_ws(" ","first_name","last_name"))\
        .withColumn("street",df1.address.specific["street"]).withColumn("city",df1.address.specific["city"])\
        .withColumn("state",df1.address["state"])\
        .drop("first_name","last_name","address","specific")
    
    df3 = df2.select("id","name","email","street","city","state")
    
    return df3



# COMMAND ----------

def write_file(container,output_file_path,read_df):
    output_location = container+output_file_path
    read_df.write.mode('overwrite').csv(output_location)
    

# COMMAND ----------

def main():
    container = "abfss://adfdemo@storagedemo072023.dfs.core.windows.net/"
    input_file_path = dbutils.widgets.get("staginglocation")
    output_file_path = "output"

    read_df = read_json(container,input_file_path)

    write_file(container,output_file_path,read_df)


if __name__ == "__main__":
    main()
