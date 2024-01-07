# Databricks notebook source
# keeping the cluster alive

sch = "year int, month string, passengers int"

df_input = spark.readStream.option("header", True).schema(sch).csv('/FileStore/tables/airlines')
display(df_input)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Reading file from storage

# COMMAND ----------

df = spark.read.format("delta") \
    .option("inferSchema", "true") \
    .option("header", "true") \
    .option("sep", ",") \
    .load("dbfs:/user/hive/warehouse/airlines")

display(df)

# COMMAND ----------

# check schema

df.printSchema()

# COMMAND ----------

# create a view

df.createOrReplaceTempView("airlines_temp_view")

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select * from airlines_temp_view;

# COMMAND ----------

# presist the dataframe in permanent storage

df.write.format("parquet").saveAsTable("airlines_parquet")

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select * from airlines_parquet;

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Renaming the columns

# COMMAND ----------

# method 1 (using withColumnRenamed() )

#renaming single column

df1 = df.withColumnRenamed("Name", "Airline Name")
df1.show()

# COMMAND ----------

# renaming multiple columns

df2 = df.withColumnRenamed("Name", "Airline Name").withColumnRenamed("Active", "Status")

df2.show()

# COMMAND ----------

# method 2 (using selectExpr() function)
# selectExpr() select only the specified columns. Throws error while working with column names having space
df3 = df.selectExpr("Name", "IATA")
df3.show()

# COMMAND ----------

df3 = df.selectExpr("Name as Airlines Name", "IATA")
df3.show()

# COMMAND ----------

df3 = df.selectExpr("Name as Airlines_Name", "IATA")
df3.show()

# COMMAND ----------

# method 3 (using select() & col() )
from pyspark.sql.functions import col

df4 = df.select(col("Name"), col("IATA"))
df4.show(5)

# COMMAND ----------

df4 = df.select(col("Name").alias("Airline Name"), col("IATA"), col("Active").alias("Status"))
df4.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Adding new columns to the dataframe

# COMMAND ----------

# method 1 (using lit() )

from pyspark.sql.functions import lit

df5 = df.withColumn("Airplane Model", lit("Airbus A320"))
df5.show(5)

# COMMAND ----------

# method 2

for i in range(df.select("Name").count()):
    pass
df6 = df.withColumn("X", lit(i))
df6 = df6.withColumn("Y", lit(i//2))
df6 = df6.withColumn("Prod", lit(col("X")*col("Y")))
df6.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Filtering from dataframe

# COMMAND ----------

df.filter(df.Name == "135 Airways").show()

# COMMAND ----------

from pyspark.sql.functions import col

df.filter(col("Name") == "135 Airways").show()

# COMMAND ----------

df.filter((col("Name")=="135 Airways") | (col("Country")=="Russia")).show()

# COMMAND ----------

df.filter((col("Name")=="135 Airways") & (col("Country")=="Russia")).show()

# COMMAND ----------

df.filter(col("Country") != "Russia").show()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Sorting the dataframe

# COMMAND ----------

# method 1 (using sort() function )

df.sort(df.Name).show()

# COMMAND ----------

df.sort(col("Name").desc()).show()

# COMMAND ----------

# method2 (using orderBy() )

df.orderBy(df.Name).show()

# COMMAND ----------

df.orderBy(col("Name").desc()).show()

# COMMAND ----------

# sorting via multiple columns

df.sort(col("Name"), col("Country")).show(10)

# COMMAND ----------

df.sort(col("Country"), col("Name")).show(10)

# COMMAND ----------

df.sort(col("Country"), col("Name").desc()).show(50)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Removing duplicate values from dataframe

# COMMAND ----------

# create a dataframe with duplicate records

columns = ["language","users_count", "version"]
data = [("Java", "20000", "4.8"), ("Python", "100000", "3.7"), ("Scala", "3000", "2.1"), ("Java", "20000", "4.8"), ("Python", "15000", "3.9")]

df8 = spark.createDataFrame(data=data, schema=columns)
display(df8)

# COMMAND ----------

# method 1 (using distinct() )
# distinct() checks all the columns, removes only if all the columns are same

df8.distinct().show()

# COMMAND ----------

# method 2 (using dropDuplicates() )
# can check specfic columns too

df8.dropDuplicates(["language"]).show()

# COMMAND ----------

df8.dropDuplicates(["version"]).show()

# COMMAND ----------

df8.dropDuplicates(["language", "version"]).show()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Using groupBy()

# COMMAND ----------

columns = ["ID", "Name", "Marks"]

data = [(1, "Vishal", 60), (2, "Utkarsh", 50), (1, "Vishal", 80), (3, "Sunil", 20), (2, "Utkarsh", 30)]

df9 = spark.createDataFrame(data=data, schema=columns)

display(df9)

# COMMAND ----------

df9.groupBy("ID").sum("Marks").show()

# COMMAND ----------

df9.groupBy("ID", "Name").sum("Marks").show()

# COMMAND ----------

df9.groupBy("ID", "Name").max("Marks").show()

# COMMAND ----------

df9.groupBy("ID", "Name").min("Marks").show()

# COMMAND ----------

df9.groupBy("ID", "Name").avg("Marks").show()

# COMMAND ----------

sampleData = [("James","Sales","NY",90000,34,10000),
    ("Michael","Sales","NY",86000,56,20000),
    ("Robert","Sales","CA",81000,30,23000),
    ("Maria","Finance","CA",90000,24,23000),
    ("Raman","Finance","CA",99000,40,24000),
    ("Scott","Finance","NY",83000,36,19000),
    ("Jen","Finance","NY",79000,53,15000),
    ("Jeff","Marketing","CA",80000,25,18000),
    ("Kumar","Marketing","NY",91000,50,21000)
  ]

schema = ["employee_name","department","state","salary","age","bonus"]
df10 = spark.createDataFrame(data=sampleData, schema = schema)
df10.show(truncate=False)

# COMMAND ----------

df10.groupBy("department").sum("salary").show()

# COMMAND ----------

# groupby multiple columns & agg

from pyspark.sql.functions import count

df10.groupBy("department", "state").agg(count("*").alias("count")).show()

# COMMAND ----------

df10.createOrReplaceTempView("emp_temp")

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select department, max(salary) from emp_temp group by department;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select department, sum(salary) from emp_temp group by department;

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Save dataframe into csv file

# COMMAND ----------

df10.write.csv("dbfs:/user/hive/warehouse/employees.csv")

# COMMAND ----------

spark.read.format("csv").load("dbfs:/user/hive/warehouse/employees.csv").show()

# COMMAND ----------

df10.write.mode("append").csv("dbfs:/user/hive/warehouse/employees.csv")

# COMMAND ----------

spark.read.format("csv").load("dbfs:/user/hive/warehouse/employees.csv").show()

# COMMAND ----------

df10.write.mode("overwrite").csv("dbfs:/user/hive/warehouse/employees.csv")

# COMMAND ----------

spark.read.format("csv").load("dbfs:/user/hive/warehouse/employees.csv").show()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Merging dataframes

# COMMAND ----------

sampleData = [("James","Sales","NY",90000,34,10000),
    ("Michael","Sales","NY",86000,56,20000),
    ("Robert","Sales","CA",81000,30,23000),
    ("Maria","Finance","CA",90000,24,23000),
    ("Raman","Finance","CA",99000,40,24000),
  ]

schema = ["employee_name","department","state","salary","age","bonus"]
emp_df1 = spark.createDataFrame(data=sampleData, schema = schema)
emp_df1.show(truncate=False)

# COMMAND ----------

sampleData = [
    ("Scott","Finance","NY",83000,36,19000),
    ("Jen","Finance","NY",79000,53,15000),
    ("Jeff","Marketing","CA",80000,25,18000),
    ("Kumar","Marketing","NY",91000,50,21000)
  ]

schema = ["name","department","state","salary","age","bonus"]
emp_df2 = spark.createDataFrame(data=sampleData, schema = schema)
emp_df2.show(truncate=False)

# COMMAND ----------

# Method 1 (using union())
# to use union we should keep in mind that the schema of both the tables should be the same

emp_df1.union(emp_df2).show()

# COMMAND ----------

emp_df2.union(emp_df1).show()

# COMMAND ----------

emp_df1.union(emp_df1).show()

# COMMAND ----------

emp_df1.union(emp_df1).distinct().show()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### if-else condition

# COMMAND ----------

from pyspark.sql.functions import when, col

new_emp_df = emp_df1.withColumn("state_full_name", when(col("state")=="NY", "New York").when(col("state")=="CA", "California").otherwise("Unknown"))
new_emp_df.show()

# COMMAND ----------

# using select()

new_emp_df1 = emp_df1.select(col("employee_name"),col("department"),col("state"),when(col("state")=="NY", "New York").when(col("state")=="CA", "California").otherwise("Unknown").alias("full_state_name"))
new_emp_df1.show()

# COMMAND ----------

new_emp_df2 = emp_df1.select(col("*"),when(col("state")=="NY", "New York").when(col("state")=="CA", "California").otherwise("Unknown").alias("state_full_name"))
new_emp_df2.show()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Joining Dataframe

# COMMAND ----------

sampleData = [
    ("Scott","Finance","NY",83000,36,19000),
    ("Jen","Finance","NY",79000,53,15000),
    ("Jeff","Marketing","CA",80000,25,18000),
    ("Kumar","Marketing","NY",91000,50,21000)
  ]

schema = ["employee_name","department","state","salary","age","bonus"]
emp_df2 = spark.createDataFrame(data=sampleData, schema = schema)
emp_df2.show(truncate=False)

# COMMAND ----------

sampleData = [("James","Sales","NY",90000,34,10000),
    ("Michael","Sales","NY",86000,56,20000),
    ("Robert","Sales","CA",81000,30,23000),
    ("Maria","Finance","CA",90000,24,23000),
    ("Raman","Finance","CA",99000,40,24000),
  ]

schema = ["employee_name","department","state","salary","age","bonus"]
emp_df1 = spark.createDataFrame(data=sampleData, schema = schema)
emp_df1.show(truncate=False)

# COMMAND ----------

emp_df1.join(emp_df2, emp_df1.state == emp_df2.state, "inner").show()

# COMMAND ----------

emp_df1.join(emp_df2, emp_df1.state == emp_df2.state, "left").show()

# COMMAND ----------

emp_df1.join(emp_df2, emp_df1.state == emp_df2.state, "right").show()

# COMMAND ----------

emp_df1.alias("A").join(emp_df2.alias("B"), col("A.state") == col("B.state"), "inner").show()

# COMMAND ----------

emp_df1.alias("A").join(emp_df2.alias("B"), col("A.department") == col("B.department"), "inner").select(col("A.employee_name"), col("B.state")).show()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Window Functions

# COMMAND ----------

all_emp_df = emp_df1.union(emp_df2)
all_emp_df.show()

# COMMAND ----------

from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, rank, dense_rank

win = Window.partitionBy("state").orderBy("salary")
all_emp_df.withColumn("salary_row_number_by_state", row_number().over(win)).show()

# COMMAND ----------

win_rank = Window.partitionBy("state").orderBy(col("salary").desc())
all_emp_df.withColumn("salary_rank", rank().over(win_rank)).show()

# COMMAND ----------

win_dense_rank = Window.partitionBy("state").orderBy(col("salary").desc())
dense_rank_df = all_emp_df.withColumn("salary_rank", dense_rank().over(win_dense_rank))
dense_rank_df.show()

# COMMAND ----------

dense_rank_df.filter(col("salary_rank") == 2).show()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Using repartition()

# COMMAND ----------

df.write.format("parquet").mode("overwrite").save("/FileStore/tables/airlines")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/airlines")

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select * from parquet.`/FileStore/tables/airlines/part-00000-tid-3036573212398184268-fee37f5a-9fb0-474b-a19b-a5c77f60f50d-146-1.c000.snappy.parquet`;

# COMMAND ----------

df.repartition(3).write.format("parquet").mode("overwrite").save("/FileStore/tables/airlines")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/airlines")

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select count(*) from parquet.`dbfs:/FileStore/tables/airlines/part-00000-tid-872006459334780536-ddeb6ba9-f822-4fc9-bfb0-4dfc77e38fa7-150-1.c000.snappy.parquet`;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select count(*) from parquet.`dbfs:/FileStore/tables/airlines/part-00001-tid-872006459334780536-ddeb6ba9-f822-4fc9-bfb0-4dfc77e38fa7-151-1.c000.snappy.parquet`;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select count(*) from parquet.`dbfs:/FileStore/tables/airlines/part-00002-tid-872006459334780536-ddeb6ba9-f822-4fc9-bfb0-4dfc77e38fa7-152-1.c000.snappy.parquet`;

# COMMAND ----------

display(df)

# COMMAND ----------

df.write.format("parquet").partitionBy("Active").mode("overwrite").save("/FileStore/tables/airlines1")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/airlines1")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/airlines1/Active=N")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/airlines1/Active=Y")

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Using partitionBy()

# COMMAND ----------

sampleData = [
    ("Scott","Finance","NY",83000,36,19000),
    ("Jen","Finance","NY",79000,53,15000),
    ("Jeff","Marketing","CA",80000,25,18000),
    ("Kumar","Marketing","NY",91000,50,21000),
    ("James","Sales","NY",90000,34,10000),
    ("Michael","Sales","NY",86000,56,20000),
    ("Robert","Sales","CA",81000,30,23000),
    ("Maria","Finance","CA",90000,24,23000),
    ("Raman","Finance","CA",99000,40,24000)
  ]

schema = ["employee_name","department","state","salary","age","bonus"]
emp_df = spark.createDataFrame(data=sampleData, schema = schema)

# COMMAND ----------

display(emp_df)

# COMMAND ----------

emp_df.write.option("header", "true").mode("overwrite").csv("/FileStore/tables/emp_data")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/emp_data")

# COMMAND ----------

emp_df.write.option("header", "true").partitionBy("state").mode("overwrite").csv("/FileStore/tables/emp_data")


# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/emp_data")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/emp_data/state=CA")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/emp_data/state=NY")

# COMMAND ----------

# column / columns on which the partition is made is not save in the part files

spark.read.option("header", "true").format("csv").load("/FileStore/tables/emp_data/state=CA").show()


# COMMAND ----------

# column / columns on which the partition is made is not save in the part files

spark.read.option("header", "true").format("csv").load("/FileStore/tables/emp_data/state=NY").show()


# COMMAND ----------

emp_df.write.option("header", "true").partitionBy("department", "state").mode("overwrite").csv("/FileStore/tables/emp_data")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/emp_data")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/emp_data/department=Finance/")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/emp_data/department=Marketing/")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/emp_data/department=Sales/")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/emp_data/department=Finance/state=CA")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/emp_data/department=Finance/state=NY")

# COMMAND ----------

spark.read.option("header", "true").csv("/FileStore/tables/emp_data/department=Finance/state=CA").show()

# COMMAND ----------

spark.read.option("header", "true").csv("/FileStore/tables/emp_data/department=Finance/state=NY").show()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Creating UDF (User Defined Functions)

# COMMAND ----------

def convertcase(val):
    c = ""
    for i in val:
        if i.islower():
            c = c + i.upper()
        else:
            c = c + i.lower()
    
    return c

# COMMAND ----------

emp_df.show()

# COMMAND ----------

from pyspark.sql.functions import col

emp_df.select("employee_name", convertcase(col("employee_name"))).show()

# COMMAND ----------

from pyspark.sql.functions import udf

col_convert = udf(convertcase)

# COMMAND ----------

emp_df.select("employee_name", col_convert(col("employee_name")).alias("Case Converted")).show()

# COMMAND ----------

emp_df.select("employee_name", col_convert(col("employee_name")), col_convert(col("department")).alias("converted_department")).show()

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select * from airlines;

# COMMAND ----------

# use udf in sql

spark.udf.register("case_convert_sql", convertcase)

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select case_convert_sql(Active) from airlines;

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Using cast()

# COMMAND ----------

sampleData = [("1", "Vishal", "100"), ("2", "Raj", "200"), ("3", "Batman", "300")]

schema = ["id", "name", "salary"]

df = spark.createDataFrame(data = sampleData, schema = schema)
df.show()

# COMMAND ----------

df.printSchema()

# COMMAND ----------

df = df.withColumn("id", df.id.cast("int"))
df.show()
df.printSchema()

# COMMAND ----------

df = df.withColumn("id", df.id.cast("int")).withColumn("salary", df.salary.cast("int"))
df.show()
df.printSchema()

# COMMAND ----------

sampleData = [("1", "Vishal", "100"), ("2", "Raj", "200"), ("3", "Batman", "300")]

schema = ["id", "name", "salary"]

df = spark.createDataFrame(data = sampleData, schema = schema)
df.printSchema()

# COMMAND ----------

from pyspark.sql.functions import col

df = df.select(col("id").cast("int").alias("ID"), col("name").alias("Name"), col("salary").cast("int").alias("Salary"))

df.show()

df.printSchema()

# COMMAND ----------

sampleData = [("1", "Vishal", "100"), ("2", "Raj", "200"), ("3", "Batman", "300")]

schema = ["id", "name", "salary"]

df = spark.createDataFrame(data = sampleData, schema = schema)
df.show()

# COMMAND ----------

df = df.selectExpr('cast(id as int)', 'cast(salary as int)')

df.printSchema()

df.show()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Handling Null Values

# COMMAND ----------

sampleData = [(1, "Vishal", 100), (2, "Raj", None), (3, None, 300), (4, "Superman", None)]

schema = ["id", "name", "salary"]

df = spark.createDataFrame(data = sampleData, schema = schema)

df.show()

# COMMAND ----------

df = df.na.fill("Batman", "name")
df.show()

# COMMAND ----------

df.na.fill(150, "salary").show()

# COMMAND ----------

from pyspark.sql.functions import avg

avg_value = df.selectExpr("avg(salary) as avg_salary").collect()[0]['avg_salary']

df.na.fill(avg_value, ["salary"]).show()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Pivoting the dataframe

# COMMAND ----------

sampleData = [
    ("Scott","Finance","NY",83000,36,19000),
    ("Jen","Finance","NY",79000,53,15000),
    ("Jeff","Marketing","CA",80000,25,18000),
    ("Kumar","Marketing","NY",91000,50,21000),
    ("James","Sales","NY",90000,34,10000),
    ("Michael","Sales","NY",86000,56,20000),
    ("Robert","Sales","CA",81000,30,23000),
    ("Maria","Finance","CA",90000,24,23000),
    ("Raman","Finance","CA",99000,40,24000)
  ]

schema = ["employee_name","department","state","salary","age","bonus"]
emp_df = spark.createDataFrame(data=sampleData, schema = schema)

# COMMAND ----------

display(emp_df)

# COMMAND ----------

# in pyspark pivoting is not possible without aggregation

df_agg = emp_df.groupBy("department", "state").sum("salary", "bonus")
display(df_agg)

# COMMAND ----------

df_pivot = emp_df.groupBy("department").pivot("state").sum("salary", "bonus")
display(df_pivot)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Types of mode while reading
# MAGIC

# COMMAND ----------

# permissive -> sets the corrupted record to null

# dropmalformed -> drops the row of the corrupted record

# failfast -> throws an exception

# badRecordsPath -> Saves the bad records to the specified path

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### dbutils commands

# COMMAND ----------

# dbutils.fs.cp() -> copy file to the given location

# dbutils.fs.head() -> returns upto to the first 'maxBytes' of the data

# dbutils.fs.ls() -> lists all the directories

# dbutils.fs.mkdirs() -> creates directory if doesn't exist

# dbutils.fs.mv() -> moves a file or directory from one location to another

# dbutils.fs.put() -> writes the given string to a file

# dbutils.fs.rm() -> removes file or directory

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### insertInto()

# COMMAND ----------

sampleData = [("1", "Vishal", "100"), ("2", "Raj", "200"), ("3", "Batman", "300")]

schema = ["id", "name", "salary"]

df = spark.createDataFrame(data = sampleData, schema = schema)
df.show()

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC create table emp(
# MAGIC   id int,
# MAGIC   name varchar(20),
# MAGIC   salary int
# MAGIC );

# COMMAND ----------

df.write.insertInto("emp")

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select * from emp;

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### collect() vs select()

# COMMAND ----------

# collect() method retrieves all the data from DataFrame as an array in the driver program. 
# This can lead to memory issues if the DataFrame is huge.
 
df.collect()

# select() method is used to select one or more columns from a DataFrame. 
# It returns a new DataFrame with the selected columns.
 
df_new = df.select("name", "salary")


# COMMAND ----------

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("create_df").getOrCreate()

data = [("John", 25), ("Lisa", 30), ("Charlie", 35), ("Mike", 40), ("Jude", 45)]
columns = ["name", "age"]

df = spark.createDataFrame(data=data, schema=columns)
df


# COMMAND ----------

df.collect()

# COMMAND ----------

for i in df.collect():
    print(f"Name is {i.name} and age is {i.age}")

# COMMAND ----------

df.collect()[0:2]

# COMMAND ----------

df.select()

# COMMAND ----------

df.select("*").show()

# COMMAND ----------

df.select("name").show()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Working with json files

# COMMAND ----------

spark.read.option("header", "true").text("/FileStore/tables/ny_city.json").show()

# COMMAND ----------

ny_city = spark.read.option("header", "true").option("multiline", "true").json("/FileStore/tables/ny_city.json")
display(ny_city)

# COMMAND ----------

ny_city.select("collision_id", "contributing_factor_vehicle_1").show()

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC create or replace temp view ny_city_temp_view using json options("multiline" True, path '/FileStore/tables/ny_city.json')

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from ny_city_temp_view;

# COMMAND ----------

df.write.mode("overwrite").save("/FileStore/tables/ny_city_sink")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/ny_city_sink")

# getting saved in parquet format as it's by default 

# COMMAND ----------

df.write.format("json").mode("overwrite").save("/FileStore/tables/ny_city_sink_new")

# COMMAND ----------

dbutils.fs.ls("/FileStore/tables/ny_city_sink_new")


# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### _SUCCESS , _committed, _started

# COMMAND ----------

# These 3 files are created by DBFS itself in the DBFS directories

#  _started -> It depicts that the process has been stated
# _committed -> It depicts how many files got created
# _SUCCESS -> It depicts that the transfer / loading happended successfully

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Working with XML files 

# COMMAND ----------

# MAGIC %fs head '/FileStore/tables/la_city.xml'

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Filling null values

# COMMAND ----------

# Importing necessary libraries
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
from pyspark.sql import SparkSession

# Creating SparkSession object
spark = SparkSession.builder.appName('null_values').getOrCreate()

# Defining the schema of the DataFrame
schema = StructType([
    StructField('id', IntegerType(), True),
    StructField('name', StringType(), True),
    StructField('age', IntegerType(), True),
    StructField('gender', StringType(), True)
])

# Creating the DataFrame with some null values
data = [(1, 'Alice', 25, 'Female'),
        (2, None, 30, 'Male'),
        (3, 'Bob', None, 'Male'),
        (4, 'Claire', 28, None),
        (5, 'David', 35, 'Male')
       ]
df = spark.createDataFrame(data, schema=schema)
df.show()


# COMMAND ----------

df.printSchema()

# COMMAND ----------

df.fillna(27).show()

# COMMAND ----------

df.fillna("27").show()

# COMMAND ----------

df.fillna("Vishal").show()

# COMMAND ----------

df.fillna("Vishal", subset="name").show()

# COMMAND ----------

df.fillna(23, subset="age").show()

# COMMAND ----------

df.fillna("Male", subset="gender").where(df.id =="4").show()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Map Transformation

# COMMAND ----------

# map() trasformation is used to apply any comlex operations like adding a col, updating a column, transforming the data etc.

# The no of input rows == no of output rows

# df needs to be converted to rdd

# narrow transformation bcz shuffling doesn't happen

# COMMAND ----------

display(df)

# COMMAND ----------

df = df.fillna(23, subset="age")
df.show()

# COMMAND ----------

mapped_df = df.rdd.map(lambda x : (x[0], x[1], x[2]+5, x[3]))
mapped_df.collect()

# COMMAND ----------

new_df = mapped_df.toDF([ "id", "name", "age", "gender"])
new_df.show()

# COMMAND ----------

def update_age(x):
    return x.id, x.name, x.age+5, x.gender

# COMMAND ----------

mapped_df = df.rdd.map(lambda x :update_age(x))
mapped_df.collect()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### cache() & persist()

# COMMAND ----------

# cache() is a shorthand for persist(StorageLevel.MEMORY_ONLY)
# persist() allows for more control of the storage level and parameters, such as MEMORY_ONLY, MEMORY_AND_DISK, DISK_ONLY,
# and the option to set replication and serialization
# cache() and persist() both persist the RDD in memory for faster access, but persist() allows for more options and customization


# COMMAND ----------

# Example using cache() function

mapped_df = df.rdd.map(lambda x :update_age(x))
mapped_df.cache()
mapped_df.count()

# COMMAND ----------

# Example using persist() function

from pyspark import StorageLevel

mapped_df = df.rdd.map(lambda x :update_age(x))
mapped_df.persist(StorageLevel.DISK_ONLY)
mapped_df.count()

# COMMAND ----------

mapped_df = df.rdd.map(lambda x :update_age(x))
mapped_df.persist(StorageLevel.MEMORY_ONLY)
mapped_df.count()

# COMMAND ----------

mapped_df = df.rdd.map(lambda x :update_age(x))
mapped_df.persist(StorageLevel.MEMORY_AND_DISK)
mapped_df.count()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Connect to blob storage using SAS token

# COMMAND ----------

# spark.conf.set(f"fs.azure.sas.{container}.{storageAccountName}.blob.core.windows.net", saskey)

# wasbs://{container}@{storageAccountName}.blob.core.windows.net

# COMMAND ----------

spark.conf.set(f"fs.azure.sas.upstream.vs17storage.blob.core.windows.net", "saskey")

# COMMAND ----------

dbutils.fs.ls("wasbs://upstream@vs17storage.blob.core.windows.net")

# COMMAND ----------

ny_city = spark.read.format("json").option("header", "true").option("multiline", "true").load("wasbs://upstream@vs17storage.blob.core.windows.net/ny-city.json")
display(ny_city)

# COMMAND ----------

ny_city_transformed = ny_city.fillna("Unknown")
display(ny_city_transformed)

# COMMAND ----------

ny_city_transformed.write.mode("overwrite").format("parquet").save("wasbs://upstream@vs17storage.blob.core.windows.net/output")

# COMMAND ----------

ny_city_transformed.write.mode("overwrite").format("parquet").save("wasbs://downstream@vs17storage.blob.core.windows.net/output")

# COMMAND ----------

display(spark.read.format("parquet").load("wasbs://downstream@vs17storage.blob.core.windows.net/output/part-00000-tid-303044258587521285-a4aad4ba-68b9-4434-a61b-1a5f2c364a16-8-1.c000.snappy.parquet"))

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Connecting to blob using access key

# COMMAND ----------

# config key -> fs.azure.account.key.{storage-account-name}.blob.core.windows.net


dbutils.fs.mount(
    source = "wasbs://{container}@{storageAccountName}.blob.core.windows.net/",
    mount_point = "mnt/raw_blob",
    extra_configs = Map("<conf-key>" -> dbutils.secrets.get(
        scope = "<scope-name>",
        key = "<key-name>")
    ) 
)

# if no scope and key remove map() & secrets

dbutils.fs.mount(
    source = "wasbs://{container}@{storageAccountName}.blob.core.windows.net/",
    mount_point = "mnt/raw_blob",
    extra_configs = {"<conf-key>":"<access_key>"}
)

# COMMAND ----------

dbutils.fs.unmount()

# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------


