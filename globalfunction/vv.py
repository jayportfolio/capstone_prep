import pandas as pd
import sys
import os

sys.path.append('../../globalfunction')  # setting path
import globalfunction.pp as pp  # importing

MIN_PRICE = 100000
MAX_PRICE = 600000
VERSION_LATEST = 'v0021_300622'
# VERSION_ACCEPTABLE = [VERSION_LATEST, 'v0021_220622', 'v0012_220622', 'v0011_210622', 'v0010_210622', 'v0006_160622', 'v0007_170622', 'v0008_190622', 'v0009_200622']
VERSION_ACCEPTABLE = [VERSION_LATEST, 'v0021_220622']

# MAX_LISTINGS = 100
# MAX_LISTINGS = 75
# MAX_LISTINGS = 40
MAX_LISTINGS = 30

# MAX_LISTINGS = 15

LISTING_ENRICHED_FILE = "../scraped/working/listings_data_enriched.csv"
LISTING_BASIC_FILE = "../scraped/working/listings_data_basic.csv"
LISTING_AGE_FILE = "../scraped/working/listings_data_age.csv"
LISTING_AGE_FILE1 = "../scraped/working/listings_data_age1.csv"

LISTING_JSON_MODEL_FILE = "../scraped/working/listings_data_jsonmodel.csv"
LISTING_JSON_MODEL_TRIAL = "../scraped/working/listings_data_jsonmodel_trial.csv"
LISTING_JSON_MODEL_FAILED = "../scraped/working/listings_data_jsonmodel_failed.csv"

LISTING_JSON_MODEL_BID_FILE = "../scraped/working/listings_data_jsonmodel__bids_only.csv"
LISTING_JSON_MODEL_BID_TRIAL = "../scraped/working/listings_data_jsonmodel__bids_only_trial.csv"
LISTING_JSON_MODEL_BID_FAILED = "../scraped/working/listings_data_jsonmodel__bids_only_failed.csv"

LISTING_JSON_META_FILE = "../scraped/working/listings_data_jsonmeta.csv"

LISTING_ENRICHED_STABLE = "../scraped/working/check1/listings_data_enriched.csv"
LISTING_BASIC_STABLE = "../scraped/working/check1/listings_data_basic.csv"
LISTING_JSON_MODEL_STABLE = "../scraped/working/check1/listings_data_jsonmodel.csv"
LISTING_JSON_MODEL_BID_STABLE = "../scraped/working/check1/listings_data_jsonmodel__bids_only.csv"
LISTING_JSON_META_STABLE = "../scraped/working/check1/listings_data_jsonmeta.csv"

# LISTING_JSONANALYTICS_FILE = "./scraped/working/listings_data_jsonanalytics.csv"

LISTING_ENRICHED_PUBLICATION = "../scraped/publish/listings_publish_enriched.csv"
LISTING_BASIC_PUBLICATION = "../scraped/publish/listings_publish_basic.csv"

LISTING_COMBINED_FILE = "../scraped/working/listings_data_combined.csv"
QUICK_COMBINED_FILE = "../scraped/working/listings_data_quick.csv"

AUDIT_FILE = "../scraped/working/ww_audit.json"
WORDCLOUD_FILE = "../scraped/working/ww_worldcloud.json"
REMOVED_FILE = "../scraped/working/ww_removed.csv"
CORRUPT_FILE = "../scraped/working/ww_corrupt.csv"

MODEL = "window.PAGE_MODEL"
MODEL2 = "window.jsonModel"


# numeric_values_only=True ==> False
def cached_data(iteration_code):
    project_root = os.path.dirname(os.path.dirname(__file__))
    output_path = os.path.join(project_root, 'scrape_site/datasets/data/')
    df = pd.read_csv(f"{output_path}data__{iteration_code}.csv")
    return df


def dataset_modelling_version(iteration_code, early_duplicates=True, HOW='left', feature_columns=None, show_not_used=False, row_limit=None,verbose=False,GET_CACHED = False):
    # print(pd.options.display.max_rows)  # 60
    orig_max_rows = pd.options.display.max_rows
    pd.options.display.max_rows = 4000
    pd.options.display.max_seq_items = 2000

    df_original = get_combined_dataset(HOW, early_duplicates, row_limit=row_limit)

    #print("type", type(df_original.columns))
    droppable_columns = []

    if iteration_code < "0010":

        if iteration_code == "0000_00000000":

            if feature_columns:
                columns = ['Price']
                columns.extend(feature_columns)

                df_original = df_original[columns]
                return df_original
            # return df_original
            else:
                #print(df_original.columns)
                print("!!!")
                return

        elif iteration_code == "0001_20220620":  # The numeric data
            df = df_original[['bedrooms_model', 'bathrooms_model', 'Price']]
            if verbose:
                print(df.columns)
            return df, "basic model: bedrooms and bathrooms", ['bedrooms_model', 'bathrooms_model'], []

    else:
        df_original = pre_tidy_dataset(df_original)

        if iteration_code < "0020":

            if iteration_code == "0010_00000000":
                df = df_original
            elif iteration_code == "0011_20220703":  # The numeric data
                # for each, i in zip(df_original.columns, range(len(df_original.columns))):
                # if df_original[each].dtype in [int, float]:print("numeric: ", each)
                # else:print("other: ", each, df_original[each].dtype);droppable_columns.append(each)
                df = df_original[pp.useful_numeric.keys()]
                description = "small series of numeric keys"
                numeric_keys = pp.useful_numeric.keys()
                cat_keys = []

            elif iteration_code == "0012_20220704":
                iteration_keys = list(pp.useful_numeric.keys())
                iteration_keys.append("borough_name")
                df = df_original[iteration_keys]
                # for column in ['type', 'compass', 'hold_type2']:
                for column in ['borough_name']:
                    df = pd.concat([df, pd.get_dummies(df[column], prefix=column)], axis=1)
                    df.drop([column], axis=1, inplace=True)  # now drop the original column (you don't need it anymore),

                numeric_keys = pp.useful_numeric.keys()
                cat_keys = ["borough_name"]

            elif iteration_code == "0013_20220704":
                iteration_keys = list(pp.useful_numeric.keys())
                cat_keys = ["borough_name", 'analyticsProperty.propertyType', 'propertySubType', 'coarse_compass_direction', 'tenure.tenureType']
                iteration_keys.extend(cat_keys)
                df = df_original[iteration_keys]
                for column in cat_keys:
                    df = pd.concat([df, pd.get_dummies(df[column], prefix=column)], axis=1)
                    df.drop([column], axis=1, inplace=True)  # now drop the original column (you don't need it anymore),
            elif iteration_code == "0014_20220708":
                iteration_keys = list(pp.useful_numeric.keys())
                cat_keys = ["borough_name", 'analyticsProperty.propertyType', 'propertySubType', 'coarse_compass_direction', 'tenure.tenureType']
                iteration_keys.extend(cat_keys)
                df = df_original[iteration_keys]
                # for column in cat_keys:
                #    df = pd.concat([df, pd.get_dummies(df[column], prefix=column)], axis=1)
                #    df.drop([column], axis=1, inplace=True)  # now drop the original column (you don't need it anymore),

                numeric_keys = pp.useful_numeric.keys()

            else:
                raise LookupError(iteration_code + " is not a valid iteration code (1)")
        elif iteration_code < "0050":
            if iteration_code in ("0031_20220709", "0041_20220710"):
                iteration_keys = list(pp.useful_numeric.keys())

                if iteration_code == "0041_20220710":
                    iteration_keys.append('property_age')

                cat_keys = ["borough_name", 'analyticsProperty.propertyType', 'propertySubType', 'coarse_compass_direction', 'tenure.tenureType']
                iteration_keys.extend(cat_keys)
                text_columns = ['bullet_points', 'long_description']
                iteration_keys.extend(text_columns)
                df = df_original[iteration_keys]

                for column in cat_keys:
                    df = pd.concat([df, pd.get_dummies(df[column], prefix=column)], axis=1)
                    df.drop([column], axis=1, inplace=True)  # now drop the original column (you don't need it anymore),

                df['content'] = df['bullet_points'] + df['long_description']

                import json
                with open(WORDCLOUD_FILE) as f:
                    raw_json = f.read()
                # print("Data type before reconstruction : ", type(raw_audit))
                # reconstructing the data as a dictionary
                df_words = json.loads(raw_json)

                for each in df_words:
                    # k += 1
                    # if k > 2: break
                    if verbose:
                        print(each)
                    label = 'content__' + each.replace(" ", "_")
                    df[label] = df["content"].str.contains(each)
                if verbose:
                    print(df.columns)
                df.drop(text_columns, axis=1, inplace=True)  # now drop the original column (you don't need it anymore),
                df.drop(['content'], axis=1, inplace=True)  # now drop the original column (you don't need it anymore),
            elif iteration_code in ("0042_20220710"):
                iteration_keys = list(pp.useful_numeric.keys())

                iteration_keys.append('property_age')

                cat_keys = ["borough_name", 'analyticsProperty.propertyType', 'propertySubType', 'coarse_compass_direction', 'tenure.tenureType']
                iteration_keys.extend(cat_keys)
                df = df_original[iteration_keys]

                for column in cat_keys:
                    df = pd.concat([df, pd.get_dummies(df[column], prefix=column)], axis=1)
                    df.drop([column], axis=1, inplace=True)  # now drop the original column (you don't need it anymore),

                if verbose:
                    print(df.columns)
        elif iteration_code < "0060":
            if iteration_code == ("0051_20220716"):
                iteration_keys = list(pp.useful_numeric.keys())
                cat_keys = ["borough_name", 'analyticsProperty.propertyType', 'propertySubType', 'coarse_compass_direction', 'tenure.tenureType']

                iteration_keys.extend(cat_keys)

                df = df_original[iteration_keys]
            elif iteration_code == ("0052_20220716"):
                description = "Shared ownership houses predict significantly higher than they should. I'm including analyticsProperty.priceQualifier"
                numeric_keys = pp.useful_numeric.keys()
                iteration_keys = list(numeric_keys)
                cat_keys = ["borough_name", 'analyticsProperty.propertyType', 'propertySubType', 'coarse_compass_direction', 'tenure.tenureType',
                            'analyticsProperty.priceQualifier']

                iteration_keys.extend(cat_keys)
                df = df_original[iteration_keys]

            elif iteration_code == ("0053_20220716"):
                description = "Shared ownership houses predict significantly higher than they should. I'm removing all the shared ownership properties I can find."
                numeric_keys = pp.useful_numeric.keys()
                iteration_keys = list(numeric_keys)
                cat_keys = ["borough_name", 'analyticsProperty.propertyType', 'propertySubType', 'coarse_compass_direction', 'tenure.tenureType',
                            'analyticsProperty.priceQualifier', 'keyFeatures', 'text.description']

                iteration_keys.extend(cat_keys)

                df = df_original[iteration_keys]

                if verbose:
                    print(len(df))
                # df[df['ids'].str.contains("ball")]

                for each in ["text.description", "analyticsProperty.priceQualifier", "keyFeatures"]:
                #for each in ["text.description", "keyFeatures",'Min share']:
                    for shared_indicator in ['shared ownership', '% share']:
                        df = df[~df[each].str.lower().str.contains(shared_indicator, na=False)]
                    if not each == "analyticsProperty.priceQualifier":
                        df.drop([each], axis=1, inplace=True)  # now drop the original column (you don't need it anymore),
                    if verbose:
                        print(len(df))

            else:
                raise ValueError(f"{iteration_code} doesn't seem to be set up (< 0060)")

        else:
            raise ValueError(f"{iteration_code} doesn't seem to be set up")

        # print(df.columns)

        if show_not_used:
            array = []
            for each in df_original.columns:
                if each not in df.columns:
                    array.append(each)
            if verbose:
                print("not used:", ','.join(array))

        if iteration_code < "0050" and False:
        #if iteration_code in (['0010_00000000','0011_20220703']):
            return df
        else:
            return df, description, numeric_keys, cat_keys

    pd.options.display.max_rows = orig_max_rows



def quick_data(separate_Xy=False, numeric_values_only=False, nans_forbidden=True, exceptional_nans=[], no_cuts=False,
               early_duplicates=True, remove_duplicates=False, HOW='left', publish=False, privacy=True, remove_outliers=False):
    df_original = get_combined_dataset(HOW, early_duplicates)

    df_original['Price'] = pd.to_numeric(df_original['Price'], 'coerce').dropna().astype(int)

    print(f'dataframe length: {len(df_original)}')
    # function to be applied

    # Drop: data protection
    if privacy:
        df_original = df_original.drop(['Address'], axis=1)

        if HOW != 'listings_only':
            df_original = df_original.drop(['analyticsBranch.displayAddress', 'analyticsProperty.postcode', 'analyticsProperty.customUri', 'propertyUrls.similarPropertiesUrl',
                                            'propertyUrls.nearbySoldPropertiesUrl'], axis=1)

    if publish:
        df_original = df_original.drop(['version', 'Links', 'date_scraped', 'referencing_link'], axis=1)

        # df_original['borough_name'] = df_original["borough"].str.extract("([a-zA-Z]+)")
        df_original['borough_name'] = df_original["borough"].str.extract("\('(.+)',")
        df_original = df_original.drop(['borough'], axis=1)

        if HOW != 'listings_only':
            df_original = df_original.drop(['link'], axis=1)
            df_original = df_original.drop(
                ['version_listing', 'version_model', 'version_meta', 'date_scraped_model'], axis=1)

            df_original = df_original.drop(['broadband.broadbandCheckerUrl'], axis=1)

    # df_original = df_original.rename(index=str, columns={"Station_Prox": "distance to train", 'bedrooms_model': 'bedrooms_2', 'bathrooms_model': 'bathrooms_2'})
    df_original = df_original.rename(index=str, columns={"Station_Prox": "distance_to_any_train"})

    if HOW == 'listings_only':
        return df_original

    df_original['floorplan_count'] = df_original['floorplans'].apply(get_array_length)
    df_original = df_original.drop(['floorplans'], axis=1)

    if remove_outliers:
        print(len(df_original))
        df_original = df_original[df_original["Price"] <= 600000]
        print(len(df_original))
        df_original = df_original[df_original["distance_to_any_train"] < 8]
        print(len(df_original))
        df_original = df_original[df_original["bathrooms"] < 8]
        print(len(df_original))
        df_original = df_original[df_original["floorplan_count"] < 18]
        print(len(df_original))

    if no_cuts:
        return df_original

    # Drop obvious Price duplicate ## Discovery: there was another column which directly mirrored the target ("Price") so I'm removing it
    df_original = df_original.drop(['analyticsProperty.price'], axis=1)

    # Drop: only related to data collection
    if not publish:
        df_original = df_original.drop(['version', 'version_listing', 'version_model', 'version_meta', 'referencing_link', 'date_scraped_model', 'Links', 'link'], axis=1)

    # Drop: extensive, image, or long text information
    df_original = df_original.drop(['keyFeatures', 'images', 'industryAffiliations', 'epcGraphs'], axis=1)

    # Drop: No information available, it seems
    df_original = df_original.drop(['feesApply', 'lettings', 'prices.message', 'countryGuide'], axis=1)
    df_original = df_original.drop(
        ['analyticsBranch.branchPostcode', 'analyticsProperty.selectedPrice', 'livingCosts.domesticRates', 'brochures'],
        axis=1)

    # Drop: Entire element is of no (immediate) use
    droppable_column, drop_rows_instead = [], []
    for each in df_original.columns:
        if each.startswith('contactInfo.') \
                or each.startswith('text.') \
                or each.startswith('misInfo.') \
                or each.startswith('date_scrape') \
                or each.startswith('dfpAdInfo.') \
                or (each.startswith('address.') and each not in ['address.outcode']) \
                or (each.startswith('location.') and each not in ['location.latitude', 'location.longitude']) \
                :
            droppable_column.append(each)

    if numeric_values_only:
        for each in df_original.columns:
            if df_original[each].dtype in [int, float] or each in ['Price']:
                pass
            else:
                droppable_column.append(each)

    if nans_forbidden:
        # Drop: has NAs
        for each in df_original.columns:
            na_count = df_original[each].isnull().sum()
            if na_count == 0 or each in exceptional_nans:
                pass
            elif na_count < len(df_original) // 3:
                print(f"allowing {each} to pass with {na_count} nulls/NANs")
                drop_rows_instead.append(each)
            else:
                print(f"dropping {each} because {na_count} nulls/NANs is too many")
                droppable_column.append(each)

    # df_original = df_original.drop(drop_rows_instead)
    for drop_rows_for in drop_rows_instead:
        df_original = df_original[df_original[drop_rows_for].notna()]
    df_original = df_original.drop(droppable_column, axis=1)
    # df_original[drop_rows_instead].dropna(inplace=True)

    if separate_Xy:
        y = df_original['Price']
        X = df_original.drop(['Price'], axis=1)
        return X, y
    else:
        return df_original


def pre_tidy_dataset(property_dataset):

    property_dataset['Price'] = pd.to_numeric(property_dataset['Price'], 'coerce').dropna().astype(int)

    # do any necessary renames, and some preliminary feature engineering
    try:
        property_dataset = property_dataset.rename(index=str, columns={"Station_Prox": "distance_to_any_train"})
    except:
        pass

    try:
        property_dataset['floorplan_count'] = property_dataset['floorplans'].apply(get_array_length)
    except:
        pass

    try:
        property_dataset['borough_name'] = property_dataset["borough"].str.extract("\('(.+)',")
    except:
        pass

    try:
        property_dataset['coarse_compass_direction'] = property_dataset["address.outcode"].str.extract("([a-zA-Z]+)")
    except:
        pass

    try:
        property_dataset['sq_ft'] = property_dataset["size"].str.extract("(\d*) sq. ft.")
    except:
        pass

    # try:
    # except:
    #     pass

    # property_dataset['type'] = property_dataset[\"Description\"].str.extract(\"(house|apartment|flat|maisonette)\")
    # property_dataset['hold_type2'] = property_dataset[\"hold_type\"].str.replace(\"Tenure:\",\"\").str.strip()

    return property_dataset

def write_export(property_dataset, version_number):
    project_root = os.path.dirname(os.path.dirname(__file__))
    output_path = os.path.join(project_root, 'scrape_site/datasets/data/')

    print("Hello again!")
    property_dataset = property_dataset.reset_index().drop('ids',axis=1)
    if len(property_dataset) > 5000:
        print("Sampling because dataset exceeds max")
        property_dataset = property_dataset.sample(n=5000)
    property_dataset.to_csv(f"{output_path}data__{version_number}.csv", index=False)

def tidy_dataset(property_dataset, coerce_to_int=None, coerce_to_float=None, na_infer_median=None, na_drop_column=None, na_drop_rows=None):

    #remove_outliers
    try:
        property_dataset = property_dataset[property_dataset["distance_to_any_train"] < 8]
    except:
        pass
    try:
        property_dataset = property_dataset[property_dataset["bathrooms"] < 8]
    except:
        pass
    try:
        property_dataset = property_dataset[property_dataset["floorplan_count"] < 18]
    except:
        pass

    # select the price range to consider
    property_dataset = property_dataset[property_dataset['Price'] >= 100000]
    property_dataset = property_dataset[property_dataset['Price'] <= 600000]

    if coerce_to_int is not None:
        for each in coerce_to_int:
            property_dataset[each] = pd.to_numeric(property_dataset[each], 'coerce').dropna().astype(int)

    if coerce_to_float is not None:
        for each in coerce_to_float:
            property_dataset[each] = pd.to_numeric(property_dataset[each], 'coerce').dropna().astype(float)

    if na_infer_median is not None:
        for each in na_infer_median:
            median_each = property_dataset[each].median()
            property_dataset[each].fillna(median_each, inplace=True)

    if na_drop_rows is not None:
        for each in na_drop_rows:
            property_dataset[each].dropna(inplace=True)

    if na_drop_column is not None and len(na_drop_column) > 0:
        for each in na_drop_column:
            if (each in property_dataset.columns) and (len(property_dataset[each].isnull()) > 0):
                try:
                    property_dataset = property_dataset.drop(each, axis=1)
                except:
                    pass

    return property_dataset


def scale_dataset(property_dataset):
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    num_pipeline = Pipeline([
        ('std_scaler', StandardScaler())
    ])
    property_dataset = num_pipeline.fit_transform(property_dataset)
    return property_dataset


def dataset_numerify_columns(df_original, columns):
    for each_column in columns:
        df_original[each_column] = pd.to_numeric(df_original[each_column], 'coerce').dropna().astype(int)
    return df_original


def prettify_dataset(df_original):
    df_original['floorplan_count'] = df_original['floorplans'].apply(get_array_length)
    df_original['borough_name'] = df_original["borough"].str.extract("\('(.+)',")
    df_original['coarse_compass_direction'] = df_original["address.outcode"].str.extract("([a-zA-Z]+)")
    # df_original['type'] = df_original[\"Description\"].str.extract(\"(house|apartment|flat|maisonette)\")
    df_original['sq_ft'] = df_original["size"].str.extract("(\d*) sq. ft.")

    return df_original


def get_combined_dataset(HOW, early_duplicates, row_limit=None,verbose=False):
    df_list = pd.read_csv(LISTING_BASIC_FILE)
    df_indiv = pd.read_csv(LISTING_ENRICHED_FILE)
    df_meta = pd.read_csv(LISTING_JSON_META_FILE)
    df_json1 = pd.read_csv(LISTING_JSON_MODEL_FILE)  # EDIT 29-06-2022: There are bid listings and regular listings. I scrape them seporately and join them here.
    df_json2 = pd.read_csv(LISTING_JSON_MODEL_BID_FILE)
    df_json = pd.concat([df_json1, df_json2], axis=0, ignore_index=True)
    df_age = pd.read_csv(LISTING_AGE_FILE)

    df_meta['id_copy'] = df_meta['id_copy'].astype(int)
    df_json['id'] = df_json['id'].astype(int)
    df_list.set_index(['ids'], inplace=True)
    df_indiv.set_index(['ids'], inplace=True)
    df_meta.set_index(['id_copy'], inplace=True)
    df_json.set_index(['id'], inplace=True)
    df_age.set_index(['ids'], inplace=True)

    if early_duplicates:
        before_arr, after_arr = [], []
        before_arr.append(len(df_list))
        df_list = df_list[~df_list.index.duplicated(keep='last')]
        after_arr.append(len(df_list))

        before_arr.append(len(df_indiv))
        df_indiv = df_indiv[~df_indiv.index.duplicated(keep='last')]
        after_arr.append(len(df_indiv))

        before_arr.append(len(df_json))
        df_json = df_json[~df_json.index.duplicated(keep='last')]
        after_arr.append(len(df_json))

        before_arr.append(len(df_meta))
        df_meta = df_meta[~df_meta.index.duplicated(keep='last')]
        after_arr.append(len(df_meta))

        before_arr.append(len(df_age))
        df_age = df_age[~df_age.index.duplicated(keep='last')]
        after_arr.append(len(df_age))

        if verbose:
            print(f"remove duplicates: {'/'.join([str(x) for x in before_arr])} ==> {'/'.join([str(x) for x in after_arr])}")

    if HOW == 'no_indexes':
        df_original = df_list \
            .merge(df_indiv, on='ids', how='inner', suffixes=('', '_listing')) \
            .merge(df_json, left_on='ids', right_on='id', how=HOW, suffixes=('', '_model')) \
            .merge(df_meta, left_on='ids', right_on='id_copy', how=HOW, suffixes=('', '_meta'))
    elif HOW == 'listings_only':
        df_original = df_list
    elif HOW == 'left':  # https://www.statology.org/pandas-merge-on-index/
        df_original = df_list \
            .join(df_indiv, on='ids', how='inner', lsuffix='', rsuffix='_listing') \
            .join(df_json, how=HOW, lsuffix='', rsuffix='_model') \
            .join(df_meta, how=HOW, lsuffix='', rsuffix='_meta') \
            .join(df_age, how=HOW, lsuffix='', rsuffix='_age')
    elif HOW == 'inner':  # https://www.statology.org/pandas-merge-on-index/
        df_original = pd.merge(pd.merge(pd.merge(df_list, df_indiv, left_index=True, right_index=True, suffixes=('', '_listing'))
                                        , df_json, left_index=True, right_index=True, suffixes=('', '_model'))
                               , df_meta, left_index=True, right_index=True, suffixes=('', '_meta'))
    else:
        raise LookupError(f"no HOW parameter called {HOW}")

    # df_original.to_csv(vv.QUICK_COMBINED_FILE, mode='w', encoding="utf-8", index=True, header=True)
    del df_list
    del df_indiv
    del df_json1
    del df_json2
    del df_json
    del df_meta
    del df_age

    if row_limit and row_limit > 0:
        # return df_original[:row_limit]
        return df_original.sample(n=row_limit)
    return df_original


def get_array_length(array_string):
    try:
        array = array_string[1:-1].split(",")  # a list of strings
        return len(array)
    except:
        # print(f"failed to get array count for: {array_string}")
        pass


def get_scraper_headers():
    return {
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005 Safari/537.36'}
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36'
    }

# quick_data(numeric_values_only=True)
# quick_data(remove_duplicates=True,numeric_values_only=False,HOW='listings_only')
# print(quick_data(remove_duplicates=True,numeric_values_only=False,HOW='listings_only',publish=True))
# quick_data(remove_duplicates=True, publish=True,remove_outliers=True)

# dataset_modelling_version("0000_00000000")
# dataset_modelling_version("0013_20220704")
