import re
import pandas as pd
3
# Sample data for testing
data_s = pd.DataFrame({
    'BaseCount': ["ATTTCCTGCC", "TTCGGAATTG", "GGCCAATTCC"]
})

GSize = data_s['BaseCount'].str.len()

def ssRNA(data_s, GSize):

    def str_count(data, pattern):
        return data.apply(lambda x: len(re.findall(pattern, x)))

    # Counting specific patterns
    Count_TT = str_count(data_s['BaseCount'], "TT")
    
    # Counting possible dimers
    dimer_patterns = ["TT", "TC", "CT", "CC"]
    Count_Dimers = pd.DataFrame({pattern: str_count(data_s['BaseCount'], pattern) for pattern in dimer_patterns})
    
    # Step-by-step replacement and counting
    data_TT = data_s['BaseCount'].replace("TT", "BB", regex=True)
    Count_TC = str_count(data_TT, "TC")

    data_TC = data_TT.replace("TC", "DD", regex=True)
    Count_CT = str_count(data_TC, "CT")

    data_CT = data_TC.replace("CT", "EE", regex=True)
    Count_CC = str_count(data_CT, "CC")

    data_CC = data_CT.replace("CC", "FF", regex=True)

    Dimer_Count = pd.DataFrame({'TT': Count_TT, 'TC': Count_TC, 'CT': Count_CT, 'CC': Count_CC})

    # Counting Purines with replacement sequences
    purine_patterns = [
        ("ABB", "HHH"), ("BBA", "III"), ("GBB", "JJJ"), ("BBG", "KKK"),
        ("ADD", "LLL"), ("DDA", "MMM"), ("GDD", "NNN"), ("DDG", "OOO"),
        ("AEE", "PPP"), ("EEA", "QQQ"), ("GEE", "RRR"), ("EEG", "SSS"),
        ("AFF", "UUU"), ("FFA", "VVV"), ("GFF", "WWW"), ("FFG", "XXX")
    ]

    
    data = data_CC.copy()
    purine_counts = {}

    for original, replacement in purine_patterns:
        purine_counts[original] = str_count(data, original)
        data = data.replace(original, replacement, regex=True)

    Purines_Count = pd.DataFrame(purine_counts)
    Purines_Count.columns = ["ATT", "TTA", "GTT", "TTG", "ATC", "TCA", "GTC", "TCG",
                             "ACT", "CTA", "GCT", "CTG", "ACC", "CCA", "GCC", "CCG"]

    Comb_Count = pd.concat([Dimer_Count, Purines_Count], axis=1)

    ###########################################################################
    ##############             Model Building                  ################
    ###########################################################################

    MixedTT = Comb_Count['ATT'] + Comb_Count['TTA'] + Comb_Count['GTT'] + Comb_Count['TTG']
    MixedCC = Comb_Count['ACC'] + Comb_Count['CCA'] + Comb_Count['GCC'] + Comb_Count['CCG']
    MixedTC = Comb_Count['ATC'] + Comb_Count['TCA'] + Comb_Count['GTC'] + Comb_Count['TCG']
    MixedCT = Comb_Count['ACT'] + Comb_Count['CTA'] + Comb_Count['GCT'] + Comb_Count['CTG']

    PureTT = Comb_Count['TT'] - MixedTT
    PureCC = Comb_Count['CC'] - MixedCC
    PureTC = Comb_Count['TC'] - MixedTC
    PureCT = Comb_Count['CT'] - MixedCT

    TotalTTs = MixedTT * 0.5 + PureTT
    TotalCCs = MixedCC * 0.5 + PureCC
    TotalTCs = MixedTC * 0.5 + PureTC
    TotalCTs = MixedCT * 0.5 + PureCT

    FracTTs = TotalTTs / GSize * 100
    FracCCs = TotalCCs / GSize * 100
    FracTCs = TotalTCs / GSize * 100
    FracCTs = TotalCTs / GSize * 100

    TFracts = FracTTs * FracCCs * FracTCs * FracCTs
    PNNsFV = TFracts / GSize
    PNNsFV

    D90 = 10.41 + (19983.83 * PNNsFV)
    
    return D90

# Running the function with the sample data
D90_value = ssRNA(data_s, GSize)
print(D90_value)
