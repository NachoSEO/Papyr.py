from urllib.parse import urlparse
import pandas as pd
from datetime import date

def extract_path(url):
    url_path = urlparse(url).path
    return url_path

def discrepancy_view(merged_df):
    tags_to_check = ['Title 1_compare', 'Meta Description 1_compare','Meta Robots 1_compare', 'Canonical Link Element 1_compare', 'rel="next" 1_compare', 'rel="prev" 1_compare','Inlinks_compare', 'Unique Inlinks_compare', 'Outlinks_compare', 'Unique Outlinks_compare','H1-1_compare', 'H2-1_compare', 'H2-2_compare', 'Status Code_compare']

    today = str(date.today())

    def discrepancyMaker(x):
        lista_inc = []
        for tag in tags_to_check:
            if (x[tag] == False):
                lista_inc.append(tag.replace('_compare',""))
        return lista_inc

    merged_df['Disparity'] = merged_df.apply(lambda x: discrepancyMaker(x), axis=1)

    disparity_df = merged_df[["Address", "Disparity"]]

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(path_reports + today + '-disparity-check.xlsx', engine='xlsxwriter')

    # Import dataframes into excel
    disparity_df.to_excel(writer, sheet_name='Disparity check')
    merged_df.to_excel(writer, sheet_name='RAW')

    # Save the excel
    writer.save()

def compare_sites(legacy, new):
    legacyCrawl = pd.read_excel(legacy, header=1)
    proCrawl = pd.read_excel(new, header=1)

    legacyCrawl['URL_Path'] = legacyCrawl['Address'].apply(extract_path)
    proCrawl['URL_Path'] = legacyCrawl['Address'].apply(extract_path)

    merged_df = pd.merge(legacyCrawl, proCrawl, on='Address') #for different domains with same routes (not subdomains) use on="URL_Path"
    merged_df.fillna(0, inplace=True)

    def check_tags():
        legacyCrawl_tags = legacyCrawl.keys().tolist()
        proCrawl_tags = proCrawl.keys().tolist()

        while set(legacyCrawl_tags) != set(proCrawl_tags):
            for item in legacyCrawl_tags:
                if item not in proCrawl_tags:
                    legacyCrawl_tags.remove(item)
            for item in proCrawl_tags:
                if item not in legacyCrawl_tags:
                    proCrawl_tags.remove(item)
        if 'URL_Path' in legacyCrawl_tags:
            legacyCrawl_tags.remove('URL_Path')
        for tag in legacyCrawl_tags:
            if tag == 'Address': #remove if statement for different domains with same routes (not subdomains)
                continue
            merged_df[tag + '_compare'] = merged_df[tag + '_x'] \
                == merged_df[tag + '_y']

    check_tags()
    discrepancy_view(merged_df)
    print('Done!')
    return merged_df

path = r'path-to-folder'
path_reports = path
merged_df = compare_sites(path + r"file-with-crawl-one", path + r"file-with-crawl-two")
