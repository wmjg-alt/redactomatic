import argparse
import csv
import sys
import spacy
import regex
import pandas as pd
import numpy as np

def config_args(): # add --anonymize
    parser = argparse.ArgumentParser(description='Redact call transcriptions or chat logs.')
    parser.add_argument('--column', type=int, required=True, help='the CSV column number containing the text to redact.')
    parser.add_argument('--inputfile', nargs='+', required=True, help='CSV input files(s) to redact')
    parser.add_argument('--outputfile', required=True, help='CSV output files')
    parser.add_argument('--anonymize', action='store_true', help='include to anonymize redacted data')
    return parser.parse_args()


def df_load_files(args):
    dfs = []
    for file in args.inputfile:
        print("Loading " + file + "...")
        dfs.append(pd.read_csv(file))
    df = pd.concat(dfs, ignore_index=True)
    df.iloc[:, args.column-1].replace('', np.nan, inplace=True)
    df.dropna(axis='index',subset=[df.columns[args.column-1]], inplace=True)
    return df


def load_files(args):
    texts = []
    for file in args.inputfile:
        filename = file
        print("Loading " + filename + "...")
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                texts.append(row)
    return texts


def ner_ml(df, args):
    print("Redacting named entities (ML)...")
    from spacy.lang.en import English
    nlp = spacy.load("en_core_web_sm")
    texts = df.iloc[:, args.column-1].tolist()
    new_texts = []
    for doc in nlp.pipe(texts, disable=["tagger", "parser"], n_threads=4, batch_size=1000):
        newString = doc.text
        for e in reversed(doc.ents): #reversed to not modify the offsets of other entities when substituting
            start = e.start_char
            end = start + len(e.text)
            newString = newString[:start] + "[" + e.label_ + "]" + newString[end:]  
        new_texts.append(newString)
    return new_texts

def address(texts):
    print("Redacting address (Regex)...")
    pattern = regex.compile("""(?<address1>(?>\d{1,6}(?>\ 1\/[234])?( (N(orth)?|S(outh)?)? ?(E(ast)?|W(est)?))?((?> \d+ ?(th|rd|st|nd))|(?> [A-Z](?>[a-z])+)+) (?>(?i)THROUGHWAY|TRAFFICWAY|CROSSROADS|EXPRESSWAY|BOULEVARD|CROSSROAD|EXTENSION|JUNCTIONS|MOUNTAINS|STRAVENUE|UNDERPASS|CAUSEWAY|CRESCENT|CROSSING|JUNCTION|MOTORWAY|MOUNTAIN|OVERPASS|PARKWAYS|TURNPIKE|VILLIAGE|VILLAGES|CENTERS|CIRCLES|COMMONS|CORNERS|ESTATES|EXPRESS|FORESTS|FREEWAY|GARDENS|GATEWAY|HARBORS|HIGHWAY|HOLLOWS|ISLANDS|JUNCTON|LANDING|MEADOWS|MOUNTIN|ORCHARD|PARKWAY|PASSAGE|PRAIRIE|RANCHES|SPRINGS|SQUARES|STATION|STRAVEN|STRVNUE|STREETS|TERRACE|TRAILER|TUNNELS|VALLEYS|VIADUCT|VILLAGE|ALLEE|ARCADE|AVENUE|BLUFFS|BOTTOM|BRANCH|BRIDGE|BROOKS|BYPASS|CANYON|CAUSWA|CENTER|CENTRE|CIRCLE|CLIFFS|COMMON|CORNER|COURSE|COURTS|CRSENT|CRSSNG|DIVIDE|DRIVES|ESTATE|EXTNSN|FIELDS|FOREST|FORGES|FREEWY|GARDEN|GATEWY|GATWAY|GREENS|GROVES|HARBOR|HIGHWY|HOLLOW|ISLAND|ISLNDS|JCTION|JUNCTN|KNOLLS|LIGHTS|MANORS|MEADOW|MEDOWS|MNTAIN|ORCHRD|PARKWY|PLAINS|POINTS|RADIAL|RADIEL|RAPIDS|RIDGES|SHOALS|SHOARS|SHORES|SKYWAY|SPRING|SPRNGS|SQUARE|STRAVN|STREAM|STREME|STREET|SUMITT|SUMMIT|TRACES|TRACKS|TRAILS|TUNNEL|TURNPK|UNIONS|VALLEY|VIADCT|VILLAG|ALLEE|ALLEY|ANNEX|AVENU|AVNUE|BAYOO|BAYOU|BEACH|BLUFF|BOTTM|BOULV|BRNCH|BRDGE|BROOK|BURGS|BYPAS|CANYN|CENTR|CNTER|CIRCL|CRCLE|CLIFF|COURT|COVES|CREEK|CRSNT|CREST|CURVE|DRIVE|FALLS|FERRY|FIELD|FLATS|FORDS|FORGE|FORKS|FRWAY|GARDN|GRDEN|GRDNS|GTWAY|GLENS|GREEN|GROVE|HARBR|HRBOR|HAVEN|HIWAY|HILLS|HOLWS|ISLND|ISLES|JCTNS|KNOLL|LAKES|LNDNG|LIGHT|LOCKS|LODGE|LOOPS|MANOR|MILLS|MISSN|MOUNT|MNTNS|PARKS|PKWAY|PKWYS|PATHS|PIKES|PINES|PLAIN|PLAZA|POINT|PORTS|RANCH|RNCHS|RAPID|RIDGE|RIVER|ROADS|ROUTE|SHOAL|SHOAR|SHORE|SPRNG|SPNGS|SPURS|STATN|STRAV|STRVN|SUMIT|TRACE|TRACK|TRAIL|TRLRS|TUNEL|TUNLS|TUNNL|TRNPK|UNION|VALLY|VIEWS|VILLG|VILLE|VISTA|WALKS|WELLS|ALLY|ANEX|ANNX|AVEN|BEND|BLUF|BLVD|BOUL|BURG|BYPA|BYPS|CAMP|CNYN|CAPE|CSWY|CENT|CNTR|CIRC|CRCL|CLFS|CLUB|CORS|CRSE|COVE|CRES|XING|DALE|DRIV|ESTS|EXPR|EXPW|EXPY|EXTN|EXTS|FALL|FRRY|FLDS|FLAT|FLTS|FORD|FRST|FORG|FORK|FRKS|FORT|FRWY|GRDN|GDNS|GTWY|GLEN|GROV|HARB|HIWY|HWAY|HILL|HLLW|HOLW|INLT|ISLE|JCTN|JCTS|KEYS|KNOL|KNLS|LAKE|LAND|LNDG|LANE|LOAF|LOCK|LCKS|LDGE|LODG|LOOP|MALL|MNRS|MDWS|MEWS|MILL|MSSN|MNTN|MTIN|NECK|ORCH|OVAL|PARK|PKWY|PASS|PATH|PIKE|PINE|PNES|PLNS|PLZA|PORT|PRTS|RADL|RAMP|RNCH|RPDS|REST|RDGE|RDGS|RIVR|ROAD|SHLS|SHRS|SPNG|SPGS|SPUR|SQRE|SQRS|STRA|STRM|STRT|TERR|TRCE|TRAK|TRKS|TRLS|TRLR|TUNL|VLLY|VLYS|VDCT|VIEW|VILL|VLGS|VIST|VSTA|WALK|WALL|WAYS|WELL|ALY|ANX|ARC|AVE|AVN|BCH|BND|BLF|BOT|BTM|BRG|BRK|BYP|CMP|CPE|CEN|CTR|CIR|CLF|CLB|COR|CTS|CRK|DAM|DIV|DVD|DRV|EST|EXP|EXT|FLS|FRY|FLD|FLT|FRD|FRG|FRK|FRT|FWY|GLN|GRN|GRV|HBR|HVN|HTS|HWY|HLS|ISS|JCT|KEY|KYS|KNL|LKS|LGT|LCK|LDG|MNR|MDW|MNT|MTN|NCK|OVL|PRK|PKY|PLN|PLZ|PTS|PRT|PRR|RAD|RPD|RST|RDG|RIV|RVR|RDS|ROW|RUE|RUN|SHL|SHR|SPG|SQR|SQU|STA|STN|STR|SMT|TER|TRK|TRL|VLY|VIA|VWS|VLG|VIS|VST|WAY|WLS|AV|BR|CP|CT|CV|DL|DM|DV|DR|FT|HT|HL|IS|KY|LK|LN|LF|MT|PL|PT|PR|RD|SQ|ST|UN|VW|VL|WY))( (N(orth)?|S(outh)?)? ?(E(ast)?|W(est)?)?)?)""", regex.IGNORECASE)
    new_texts = []
    for text in texts:
        new_text = pattern.sub('[ADDRESS]', text, concurrent=True)
        new_texts.append(new_text)
    return new_texts
    

def cardinal(texts):
    print("Redacting cardinal (Regex)...")
    pattern = regex.compile("""
    (?xi)           # free-spacing mode
  (?(DEFINE)
  (?<one_to_9>  
  (?:\m(one|two|three|four|five|six|seven|eight|nine)\M)
  ) # end one_to_9 definition

  (?<ten_to_19>  
  (?:\m(ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)\M) 
  ) # end ten_to_19 definition

  (?<two_digit_prefix>
  (?:\m(s(?:even|ix)|t(?:hir|wen)|f(?:if|or)|eigh|nine)ty)\M
  ) # end two_digit_prefix definition

  (?<one_to_99>
  (?&two_digit_prefix)(?:[- ](?&one_to_9))?|(?&ten_to_19)|
                                              (?&one_to_9)
  ) # end one_to_99 definition

  (?<one_to_999>
  (?&one_to_9)[ ]hundred(?:[ ](?:and[ ])?(?&one_to_99))?|
                                            (?&one_to_99)
  ) # end one_to_999 definition

  (?<one_to_999_999>
  (?&one_to_999)[ ]thousand(?:[ ](?&one_to_999))?|
                                    (?&one_to_999)
  ) # end one_to_999_999 definition

  (?<one_to_999_999_999>
  (?&one_to_999)[ ]million(?:[ ](?&one_to_999_999))?|
                                   (?&one_to_999_999)
  ) # end one_to_999_999_999 definition

  (?<one_to_999_999_999_999>
  (?&one_to_999)[ ]billion(?:[ ](?&one_to_999_999_999))?|
                                   (?&one_to_999_999_999)
  ) # end one_to_999_999_999_999 definition

  (?<one_to_999_999_999_999_999>
  (?&one_to_999)[ ]trillion(?:[ ](?&one_to_999_999_999_999))?|
                                    (?&one_to_999_999_999_999)
  ) # end one_to_999_999_999_999_999 definition

  (?<bignumber>
  ((\mzero\M|\moh\M|(?&one_to_999_999_999_999_999)))
  ) # end bignumber definition

  (?<zero_to_9>
  (?&one_to_9)
  ) # end zero to 9 definition

  (?<decimals>
  point(?:[ ](?&zero_to_9))+
  ) # end decimals definition
  
) # End DEFINE


####### The Regex Matching Starts Here ########
#(?&bignumber)(?:[ ](?&decimals))?

### Other examples of groups we could match ###
(?&bignumber)|(\d+)
# (?&one_to_99)
# (?&one_to_999)
# (?&one_to_999_999)
# (?&one_to_999_999_999)
# (?&one_to_999_999_999_999)
# (?&one_to_999_999_999_999_999)
""")
    new_texts = []
    for text in texts:
        new_text = pattern.sub('[CARDINAL]', text, concurrent=True)
        new_texts.append(new_text)
    return new_texts

def ccard(texts):
    print("Redacting credit card (Regex)...")
    pattern = regex.compile("""(?:\d[ -]*?){13,16}""", regex.IGNORECASE)
    new_texts = []
    for text in texts:
        new_text = pattern.sub('[CARD_NUMBER]', text, concurrent=True)
        new_texts.append(new_text)
    return new_texts

def clean(texts):
    print("Cleaning text (Regex)...")
    spaces = regex.compile('\s+')
    dotdot = regex.compile(r'\.\.\.')
    unknown = regex.compile(r'\<UNK\>')
    add_space = regex.compile(r'(\]\[)')
    add_space2 = regex.compile(r'((\w+)\[)')
    add_space3 = regex.compile(r'(\](\w+))')
    new_texts = []
    for text in texts:
        new_text = dotdot.sub('', text, concurrent=True)
        new_text = spaces.sub(' ', new_text, concurrent=True)
        new_text = unknown.sub('', new_text, concurrent=True)
        new_text = add_space.sub('] [', new_text, concurrent=True)
        new_text = add_space2.sub(r'\2 [', new_text, concurrent=True)
        new_text = add_space3.sub(r'] \2', new_text, concurrent=True)
        new_text = new_text.strip()
        new_texts.append(new_text)
    return new_texts

def ordinal(texts):
    print("Redacting ordinals (Regex)...")
    pattern = regex.compile("""
    (?x)           # free-spacing mode
(?(DEFINE)
  (?<one_to_9>  
  (fir|seco|thi|four|fif|six|seven|eigh|nin|[1-9])(?:st|nd|rd|th)
  ) # end one_to_9 definition

  (?<ten_to_19> 
  (?:(?:(ten|eleven|twelf)|((?:thir|four|fif|six|seven|eigh|nine)teen))th|((10|11|12|13|14|15|16|17|18|19)th))
  ) # end ten_to_19 definition

  (?<two_digit_ordinal_prefix>
  ((?:s(?:even|ix)|t(?:hir|wen)|f(?:if|or)|eigh|nine)tieth)|((2|3|4|5|6|7|8|9)0)th
  ) # end two_digit_prefix definition

  (?<two_digit_prefix>
  ((?:s(?:even|ix)|t(?:hir|wen)|f(?:if|or)|eigh|nine)ty)
  ) # end two_digit_prefix definition

  (?<numeric_ordinal>
  ([2-9][1-9](st|nd|rd|th))
  )

  (?<one_to_99>
  (?&two_digit_ordinal_prefix)|(?&numeric_ordinal)|(?&two_digit_prefix)(?:[- ](?&one_to_9))|(?&ten_to_19)|(?&one_to_9)
  ) # end one_to_99 definition

  (?<one_to_999>
  (?&one_to_9)[ ]hundred(?:[ ](?:and[ ])?(?&one_to_99))?|
                                            (?&one_to_99)
  ) # end one_to_999 definition

  (?<one_to_999_999>
  (?&one_to_999)[ ]thousand(?:[ ](?&one_to_999))?|
                                    (?&one_to_999)
  ) # end one_to_999_999 definition

  (?<one_to_999_999_999>
  (?&one_to_999)[ ]million(?:[ ](?&one_to_999_999))?|
                                   (?&one_to_999_999)
  ) # end one_to_999_999_999 definition

  (?<one_to_999_999_999_999>
  (?&one_to_999)[ ]billion(?:[ ](?&one_to_999_999_999))?|
                                   (?&one_to_999_999_999)
  ) # end one_to_999_999_999_999 definition

  (?<one_to_999_999_999_999_999>
  (?&one_to_999)[ ]trillion(?:[ ](?&one_to_999_999_999_999))?|
                                    (?&one_to_999_999_999_999)
  ) # end one_to_999_999_999_999_999 definition

  (?<bignumber>
  (?&one_to_999_999_999_999_999)
  ) # end bignumber definition

  (?<zero_to_9>
  (?&one_to_9)
  ) # end zero to 9 definition

  (?<decimals>
  point(?:[ ](?&zero_to_9))+
  ) # end decimals definition
  
) # End DEFINE


####### The Regex Matching Starts Here ########
#(?&bignumber)(?:[ ](?&decimals))?

### Other examples of groups we could match ###
(?&bignumber)
# (?&one_to_99)
# (?&one_to_999)
# (?&one_to_999_999)
# (?&one_to_999_999_999)
# (?&one_to_999_999_999_999)
# (?&one_to_999_999_999_999_999)
""", regex.IGNORECASE)
    new_texts = []
    for text in texts:
        new_text = pattern.sub('[ORDINAL]', text, concurrent=True)
        new_texts.append(new_text)
    return new_texts

def phone(texts):
    print("Redacting phone (Regex)...")
    pattern = regex.compile("""((?:(?<![\d-])(?:\+?\d{1,3}[-.\s*]?)?(?:\(?\d{3}\)?[-.\s*]?)?\d{3}[-.\s*]?\d{4}(?![\d-]))|(?:(?<![\d-])(?:(?:\(\+?\d{2}\))|(?:\+?\d{2}))\s*\d{2}\s*\d{3}\s*\d{4}(?![\d-])))""", regex.IGNORECASE)
    new_texts = []
    for text in texts:
        new_text = pattern.sub('[PHONE]', text, concurrent=True)
        new_texts.append(new_text)
    return new_texts

def zip(texts):
    print("Redacting zip (Regex)...")
    pattern = regex.compile("""(^(?<full>(?<part1>[ABCEGHJKLMNPRSTVXY]{1}\d{1}[A-Z]{1})(?:[ ](?=\d))?(?<part2>\d{1}[A-Z]{1}\d{1}))$)|((?<zip>(?!00[02-5]|099|213|269|34[358]|353|419|42[89]|51[789]|529|53[36]|552|5[67]8|5[78]9|621|6[348]2|6[46]3|659|69[4-9]|7[034]2|709|715|771|81[789]|8[3469]9|8[4568]8|8[6-9]6|8[68]7|9[02]9|987)\d{5})\-?(?<plus4>[0-9]{4})?)""", regex.IGNORECASE)
    new_texts = []
    for text in texts:
        new_text = pattern.sub('[ZIP]', text, concurrent=True)
        new_texts.append(new_text)
    return new_texts