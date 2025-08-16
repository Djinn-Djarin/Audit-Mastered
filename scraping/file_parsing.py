import pandas as pd
from rest_framework.exceptions import ValidationError

# === File Reader Classes ===

class FileReader:
    def read(self, file):
        raise NotImplementedError

class CsvFileReader(FileReader):
    def read(self, file):
        return pd.read_csv(file)

class ExcelFileReader(FileReader):
    def read(self, file):
        return pd.read_excel(file)
    

# === File Parser === 
class FileReaderFactory:
    EXTENSION_READERS = {
        ".csv": CsvFileReader,
        ".xlsx": ExcelFileReader,
    }

    @classmethod
    def get_reader(cls, filename):
        for ext, reader_cls in cls.EXTENSION_READERS.items():
            if filename.lower().endswith(ext):
                return reader_cls()
        raise ValidationError("Unsupported file format. Use .csv or .xlsx")


class FileParser:
    def __init__(self, file):
        self.reader = FileReaderFactory.get_reader(file.name)
        self.file = file

    def parse(self):
        data=  self.reader.read(self.file)
        df = pd.DataFrame(data)
        data_cleaner = DataFrameCleaner(df)
        cleaned_dataframe = data_cleaner.clean()
        return cleaned_dataframe

# === DataFrame Cleaner ===

class DataFrameCleaner:
    def __init__(self, df):
        self.df = df

    def drop_na(self):
        self.df.dropna(inplace=True)
        return self

    def reset_index(self):
        self.df.reset_index(drop=True, inplace=True)
        return self

    def clean(self):
        return self.drop_na().reset_index().df


# ====================== Still need to implement ===========================

# ===  Product ID Rule Generic Classes === 
class ProductIdRule:
    def validate(self, product_ids):
        raise NotImplementedError

class StartWithRule(ProductIdRule):
    def __init__(self, prefix):
        self.prefix = prefix

    def validate(self, product_ids):
        if self.prefix and not all(pid.startswith(self.prefix) for pid in product_ids):
            raise ValidationError(f"All product IDs must start with '{self.prefix}'.")

class LengthRule(ProductIdRule):
    def __init__(self, length):
        self.length = length

    def validate(self, product_ids):
        if not all(len(pid) == self.length for pid in product_ids):
            raise ValidationError(f"All product IDs must be exactly {self.length} characters long.")

class AlphanumericRule(ProductIdRule):
    def validate(self, product_ids):
        if not all(pid.isalnum() for pid in product_ids):
            raise ValidationError("All product IDs must be alphanumeric.")

class NumericRule(ProductIdRule):
    def validate(self, product_ids):
        if not all(pid.isdigit() for pid in product_ids):
            raise ValidationError("All product IDs must be numeric.")

class UniqueRule(ProductIdRule):
    def validate(self, product_ids):
        if product_ids.duplicated().any():
            raise ValidationError("Product IDs must be unique.")

class NotNullRule(ProductIdRule):
    def __init__(self, column_name):
        self.column_name = column_name

    def validate(self, product_ids):
        if product_ids.isnull().any():
            raise ValidationError(f"Column '{self.column_name}' contains null values.")
class ProductIdValidator:
    PLATFORM_RULES = {
        "amazon": [
            StartWithRule("B0"),
            LengthRule(10),
            AlphanumericRule(),
        ],
        "flipkart": [
            LengthRule(16),
            AlphanumericRule(),
        ],
        "myntra": [
            LengthRule(9),
            NumericRule(),
        ],
    }

    def __init__(self, df, column_name):
        self.df = df
        self.column_name = column_name

    def validate(self, audit_platform):
        rules = self.PLATFORM_RULES.get(audit_platform)
        if not rules:
            raise ValidationError(f"Unsupported audit platform: {audit_platform}")

        if self.column_name not in self.df.columns:
            raise ValidationError(f"Column '{self.column_name}' does not exist in the file.")

        product_ids = self.df[self.column_name].astype(str)
        # Always check for nulls and uniqueness
        NotNullRule(self.column_name).validate(product_ids)
        UniqueRule().validate(product_ids)

        for rule in rules:
            rule.validate(product_ids)

        return True
    