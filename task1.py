import pandas as pd 
from datetime import datetime
# task 1.1
data_df = pd.read_csv('zadanie1.csv')

# checking structure and formats
print(data_df.head(10))
print(data_df.info())

data_df['date'] = data_df['data_urodzenia'].apply(lambda date: datetime.strptime(date, '%d.%m.%Y'))

print(data_df.head(10))

limit_date = datetime(1999, 12, 31)

# task 1.2
print("Count of people who born after 1999-12-31")
print(data_df[data_df.date > limit_date].imie.count())

# task 1.3
print("All unique female names")
print(data_df[data_df['imie'].str.match(r'.*a$')].imie.unique())