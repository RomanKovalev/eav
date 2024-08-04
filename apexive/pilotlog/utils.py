import os
import json
import time
import logging
import hashlib
from collections import defaultdict
import pandas as pd
from pilotlog.models import Row, Attribute, AttributeValue, ChildAttribute

logger = logging.getLogger(__name__)


class Importer(object):
    """
    Handles data import and export.
    """

    def __init__(self, import_source, export_source):
        """
        Initialize with the given filename.
        """
        if import_source:
            self.import_source = import_source
            if not os.path.isfile(import_source):
                logger.error(f'File {import_source} not exists.')
                raise FileNotFoundError(f'File {import_source} not exists.')
        if export_source:
            self.export_dest = export_source

    def calculate_row_hash(self, row):
        """
        Calculate hash for a data row.
        """
        sorted_dict = json.dumps(row.to_dict(), sort_keys=True)
        return hashlib.sha256(sorted_dict.encode()).hexdigest()

    def cleanup_db(self):
        """
        Clean up database tables.
        """
        start_time = time.time()
        logger.info("Cleaning up database")
        Row.objects.all().delete()
        Attribute.objects.all().delete()
        AttributeValue.objects.all().delete()
        ChildAttribute.objects.all().delete()

        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Cleaning up database time: {elapsed_time} seconds")

    def load_source(self):
        """
        Load data from the file into a DataFrame.
        """
        with open(self.import_source, 'r') as file:
            json_str = file.read()
        json_str = json_str.replace('\\"', '"')
        json_data = json.loads(json_str)
        df = pd.DataFrame(json_data)
        df['table'] = df['table'].str.lower()
        df['row_hash'] = df.apply(self.calculate_row_hash, axis=1)
        return df

    def create_rows(self, df):
        """
        Create Row records in the database.
        """
        start_time = time.time()
        rows = []
        for _, row in df.iterrows():
            rows.append(Row(
                hash=row['row_hash'],
                table=row['table'],
            ))
        created_rows = Row.objects.bulk_create(rows)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Created {len(created_rows)} Rows for {elapsed_time} seconds")
        return created_rows

    def create_attributes(self, df):
        """
        Create Attribute and AttributeValue records.
        """
        logger.info("Fetching rows and populating attributes list...")
        start_time = time.time()
        attrs_value = []
        for _, row in df.iterrows():
            row_object = Row.objects.get(hash=row['row_hash'])
            list_data = row.to_dict()
            for attribute in list_data.items():
                attr = Attribute.objects.create(name=attribute[0], row=row_object)
                if not isinstance(attribute[1], dict):
                    attrs_value.append(
                        AttributeValue(
                            row=row_object,
                            attribute=attr,
                            value=attribute[1]
                        )
                    )
        created_attributes = AttributeValue.objects.bulk_create(attrs_value)  # noqa: F841
        logger.info(f'Create AttributesValues quantity: {len(attrs_value)}')
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Creating of Attributes and AttributesValues tooks: {elapsed_time} seconds")

    def create_childattributes(self, df):
        """
        Create ChildAttribute records.
        """
        logger.info("Fetching rows and populating ChildAttribute list...")
        start_time = time.time()
        child_attrs_to_create = []
        for _, row in df.iterrows():
            row_object = Row.objects.get(hash=row['row_hash'])
            list_data = row.to_dict()
            for attribute in list_data.items():
                if isinstance(attribute[1], dict):
                    try:
                        parent_attribute = Attribute.objects.get(row=row_object, name=attribute[0])  # noqa: F841
                        for child_attribute in attribute[1].items():
                            child_attrs_to_create.append(
                                ChildAttribute(
                                    name=child_attribute[0],
                                    row=row_object,
                                )
                            )
                    except Exception as e:
                        logger.error(e)
        created_attributes = ChildAttribute.objects.bulk_create(child_attrs_to_create)  # noqa: F841
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Creating of ChildAttributes tooks: {elapsed_time} seconds")
        logger.info(f'ChildAttributes created quantity: {len(child_attrs_to_create)}')

    def create_child_attrs_values(self, df):
        """
        Create AttributeValue records for ChildAttributes.
        """
        logger.info("Populating Values for ChildAttributes list...")
        start_time = time.time()
        child_attrs_values_to_create = []
        for _, row in df.iterrows():
            row_object = Row.objects.get(hash=row['row_hash'])
            list_data = row.to_dict()
            for attribute in list_data.items():
                if isinstance(attribute[1], dict):
                    parent_attribute = Attribute.objects.get(row=row_object, name=attribute[0])
                    for child_attribute in attribute[1].items():
                        child_attribute_object = ChildAttribute.objects.get(
                            name=child_attribute[0],
                            row=row_object
                        )
                        child_attrs_values_to_create.append(
                            AttributeValue(
                                row=row_object,
                                attribute=parent_attribute,
                                child_attribute=child_attribute_object,
                                value=child_attribute[1],
                            )
                        )
        end_time = time.time()
        elapsed_time = end_time - start_time
        created_attributes_values = AttributeValue.objects.bulk_create(child_attrs_values_to_create)  # noqa: F841
        logger.info(f'Values for ChildAttributes created quantity: {len(child_attrs_values_to_create)}')
        logger.info(f"Values for ChildAttributes tooks: {elapsed_time} seconds")

    def import_data(self):
        """
        Perform the entire import process.
        """
        main_start_time = time.time()
        self.cleanup_db()
        df = self.load_source()
        self.create_rows(df)
        self.create_attributes(df)
        self.create_childattributes(df)
        self.create_child_attrs_values(df)
        end_time = time.time()
        elapsed_time = end_time - main_start_time
        logger.info(f"Import tooks: {elapsed_time} seconds")

    def export_data(self):
        """
        Export data to CSV file.
        """
        logger.info('Start exporting data...')

        filename = self.export_dest

        df = pd.DataFrame(columns=["ForeFlight Logbook Import"])
        df.to_csv(filename, index=False, mode='a', header=True)

        df = pd.DataFrame(columns=[])
        df.to_csv(filename, index=False, mode='a', header=True)

        for table in Row.objects.all().distinct().values_list("table", flat=True):
            df = pd.DataFrame(columns=[f'{table.capitalize()} Table'])
            df.to_csv(filename, index=False, mode='a', header=True)

            all_rows_hashes = list(Row.objects.filter(table=table).values_list("hash", flat=True))

            attribute_values = AttributeValue.objects.select_related("attribute", "child_attribute").filter(
                row__table=table, row__hash__in=all_rows_hashes
            ).values_list("row__hash", "attribute__name", "child_attribute__name", "value")
            result_dict = defaultdict(dict)

            for hash, attribute_name, child_attribute_name, value in attribute_values:
                if child_attribute_name:
                    result_dict[hash][child_attribute_name] = value
                else:
                    result_dict[hash][attribute_name] = value
            result_dict = dict(result_dict)

            df = pd.DataFrame.from_dict(result_dict, orient='index')

            df.reset_index(inplace=True)
            df.rename(columns={'index': 'hash'}, inplace=True)
            df.drop(columns=['hash'], inplace=True)
            df.drop(columns=['row_hash'], inplace=True)
            df.drop(columns=['table'], inplace=True)

            df.to_csv(filename, index=False, mode='a', header=True)
        logger.info('Data export is finished...')
