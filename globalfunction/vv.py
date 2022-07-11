import pandas as pd
import vv

MIN_PRICE = 100000
MAX_PRICE = 600000
VERSION_LATEST = 'v0021_300622'
VERSION_ACCEPTABLE = [VERSION_LATEST, 'v0021_220622', 'v0012_220622', 'v0011_210622', 'v0010_210622', 'v0006_160622', 'v0007_170622', 'v0008_190622', 'v0009_200622']

# MAX_LISTINGS = 100
# MAX_LISTINGS = 75
# MAX_LISTINGS = 40
MAX_LISTINGS = 30


# MAX_LISTINGS = 15

LISTING_ENRICHED_FILE = "../scraped/working/listings_data_enriched.csv"
LISTING_BASIC_FILE = "../scraped/working/listings_data_basic.csv"

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
REMOVED_FILE = "../scraped/working/ww_removed.csv"
CORRUPT_FILE = "../scraped/working/ww_corrupt.csv"

MODEL = "window.PAGE_MODEL"
MODEL2 = "window.jsonModel"

# numeric_values_only=True ==> False
def dataset_modelling_version(iteration_code, separate_Xy=False, numeric_values_only=False, nans_forbidden=True, exceptional_nans=[], no_cuts=False,
               early_duplicates=True, remove_duplicates=False, HOW='left', publish=False, privacy=True, remove_outliers=False):

    pass

def quick_data(separate_Xy=False, numeric_values_only=False, nans_forbidden=True, exceptional_nans=[], no_cuts=False,
               early_duplicates=True, remove_duplicates=False, HOW='left', publish=False, privacy=True, remove_outliers=False):
    df_list = pd.read_csv(vv.LISTING_BASIC_FILE)
    df_indiv = pd.read_csv(vv.LISTING_ENRICHED_FILE)
    df_meta = pd.read_csv(vv.LISTING_JSON_META_FILE)

    df_json1 = pd.read_csv(vv.LISTING_JSON_MODEL_FILE)  # EDIT 29-06-2022: There are bid listings and regular listings. I scrape them seporately and join them here.
    df_json2 = pd.read_csv(vv.LISTING_JSON_MODEL_BID_FILE)
    df_json = pd.concat([df_json1, df_json2], axis=0, ignore_index=True)

    df_meta['id_copy'] = df_meta['id_copy'].astype(int)
    df_json['id'] = df_json['id'].astype(int)

    df_list.set_index(['ids'], inplace=True)
    df_indiv.set_index(['ids'], inplace=True)
    df_meta.set_index(['id_copy'], inplace=True)
    df_json.set_index(['id'], inplace=True)

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
            .join(df_meta, how=HOW, lsuffix='', rsuffix='_meta')
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

    if remove_duplicates:
        print(len(df_original))
        df_original = df_original[~df_original.index.duplicated(keep='last')]
        print("==>", len(df_original))

    df_original['Price'] = pd.to_numeric(df_original['Price'], 'coerce').dropna().astype(int)

    print(f'dataframe length: {len(df_original)}')
    # function to be applied


    # Drop: data protection
    if privacy:
        df_original = df_original.drop(['Address'], axis=1)

        if HOW != 'listings_only':
            df_original = df_original.drop(['analyticsBranch.displayAddress', 'analyticsProperty.postcode', 'analyticsProperty.customUri','propertyUrls.similarPropertiesUrl','propertyUrls.nearbySoldPropertiesUrl'], axis=1)

    if publish:
        df_original = df_original.drop(['version', 'Links','date_scraped', 'referencing_link'], axis=1)

        #df_original['borough_name'] = df_original["borough"].str.extract("([a-zA-Z]+)")
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

    def get_array_length(array_string):
        try:
            array = array_string[1:-1].split(",")  # a list of strings
            return len(array)
        except:
            # print(f"failed to get array count for: {array_string}")
            pass

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

#quick_data(numeric_values_only=True)
#quick_data(remove_duplicates=True,numeric_values_only=False,HOW='listings_only')
#print(quick_data(remove_duplicates=True,numeric_values_only=False,HOW='listings_only',publish=True))
quick_data(remove_duplicates=True, publish=True,remove_outliers=True)