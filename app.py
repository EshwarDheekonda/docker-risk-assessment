#Flask app (API) begins
import os
from flask import Flask,jsonify,request

app = Flask(__name__)

@app.route('/',methods=["GET"])
#app.route("/result",methods=["POST","GET"])

#Flask app (API) Ends

def apiTesting():

    #importing the neccessary libraries
    query = request.args['searchName']
    from googlesearch import search #pip install google
    import requests
    from bs4 import BeautifulSoup #pip install bs4
    import spacy 
    nlp = spacy.load("en_core_web_sm") #python -m spacy download en_core_web_sm
    import pandas as pd 
    from openpyxl import load_workbook
    import re
    from spacy.matcher import Matcher
    import json
    
    #Function to clean the text like make spaces etc
    def align_sentence(sent):
        
        sent_split = sent.split()
        result_sent_list = []
        
        for string in sent_split:
            if string.isupper() == True:
                result_sent_list.append(string)
            else:
                y = ''
                for idx,i in enumerate(string):
                    if i.isupper() == True and idx != 0:
                        #print('Inside if',i)
                        i = i.replace(i,' '+i)
                    y = y+i
                result_sent_list.append(y)
            sent_result = ' '.join(result_sent_list)
        return sent_result
    
    #Function to extract date of birth
    def dob_pattern(text):
        
        doc = nlp(text)
        list_return = []

        pattern_dob_year = [{'LOWER': 'born','POS':'VERB'}, {'POS': 'NUM','LENGTH':4}]
        pattern_dob = [{'LOWER': 'born','POS':'VERB'}, {'POS': 'NUM'},{'POS': 'PROPN'},{'POS': 'NUM'}]              

        matcher = Matcher(nlp.vocab,validate=True)

        matcher.add('Year_of_Birth',[pattern_dob_year])
        matcher.add('Date_of_Birth',[pattern_dob])

        found_matches = matcher(doc)

        if found_matches:
            for match_id,start_pos,end_pos in found_matches:
                string_id = nlp.vocab.strings[match_id]
                span = doc[start_pos:end_pos]
                list_return = [string_id,span.text[5:],start_pos,end_pos]
        else:
            pattern_born = [{'LOWER': 'born','POS':'VERB'}]            
            matcher = Matcher(nlp.vocab,validate=True)
            matcher.add('born',[pattern_born])
            first_match = matcher(doc)

            if first_match:
                pattern_dob1 = [{'POS': 'NUM'},{'POS': 'PROPN'},{'POS': 'NUM','LENGTH':4}]  
                matcher1 = Matcher(nlp.vocab,validate=True)
                matcher1.add('Date_of_Birth1',[pattern_dob1])
                found_matches = matcher1(doc)
                for match_id,start_pos,end_pos in found_matches:
                    string_id = nlp.vocab.strings[match_id]
                    span = doc[start_pos:end_pos]
                    list_return = [string_id,span.text,start_pos,end_pos]
    
        return list_return
    
    #Function to extract address
    def address_pattern(text):
        
        doc = nlp(text)
        list_return = []
        pattern_address = [{'LOWER': 'address','POS':'NOUN'}, {'LOWER':'is'},{'POS': 'NUM'},{'TAG':'NNP','OP':'+'},{'IS_PUNCT':True,'OP':'*'},
                        {'POS':'PROPN','OP':'+'},{'IS_PUNCT':True,'OP':'*'},{'POS':'PROPN','OP':'*'},{'POS':'NUM'}]           
        pattern_address1 = [{'POS':'NUM'}, {'POS': 'PROPN','OP':'*'},{'POS': 'NUM'},{'POS': 'PROPN'},{'POS': {"IN": ["NOUN", "PROPN"]}},{'POS': {"IN": ["NOUN", "PROPN"]}},
                        {'IS_PUNCT':True,'OP':'*'},{'POS': 'PROPN'},{'POS':'NUM'}]              

        matcher = Matcher(nlp.vocab,validate=True)

        matcher.add('Address',[pattern_address])
        matcher.add('Address1',[pattern_address1])

        found_matches = matcher(doc)

        for match_id,start_pos,end_pos in found_matches:
            string_id = nlp.vocab.strings[match_id]
            if string_id == 'Address':
                span = doc[start_pos+2:end_pos]
            else:
                span = doc[start_pos:end_pos] 
            list_return = [string_id,span.text,start_pos,end_pos]  

        return list_return
    
    #Function to extract social media accounts like Instagram, Facebook, LinkedIN, Twitter
    def find_social_media_acnt(inp_list,line):
        id_name_type = []
        dictSocialMedia = {"https://www.instagram.com":"Instagram ID",".linkedin.com":"LinkedIn Profile",
                           "https://www.facebook.com":"Facebook ID","twitter.com":"Twitter ID"}
        for soc_med_type in inp_list:
            li = list(line.split(' '))
            for idx,i in enumerate(li):
                if soc_med_type in i and soc_med_type != 'https://www.facebook.com': 
                    #print('li[idx+2] ',li[idx+2],'  soc_med_type  ',soc_med_type)
                    id_name_type.append([li[idx+2],dictSocialMedia[soc_med_type]])
                    break
                if soc_med_type in i and soc_med_type == 'https://www.facebook.com':
                    if li[idx+2] in ('public','people'):
                        if str(li[idx+4])[-1]:
                            id_name_type.append([li[idx+4]+li[idx+5],dictSocialMedia[soc_med_type]])
                        else:
                            id_name_type.append([li[idx+4],dictSocialMedia[soc_med_type]])
                        break
                    id_name_type.append([li[idx+2],dictSocialMedia[soc_med_type]])
        return id_name_type
        #Match found and then call the append_list function
    
    #Function to append the matches found to the resulting list   
    
    def append_list(inp_list):
        output_match_term.append(inp_list[0])
        output_word.append(inp_list[1])
        output_line.append(inp_list[2])
        output_list_span_start.append(inp_list[3])
        output_list_span_end.append(inp_list[4]) 
        output_list_search.append(inp_list[5])
        output_list_url_no.append(inp_list[6])
        output_list_line_no.append(inp_list[7]) 
        output_list_match_count.append(inp_list[8])
        
    #search_list = ['Adela williams']#
    #search_list = ['Dan Ricky','Daniel Rickenson','Manideep Bora','Adela williams','Madhu Tejasvi',
    #               'Dustin Alexander','Darrell L Jason','David Nathan','Ricky Pointing','Armond Rashad Morrison']#

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
    mod_name = 'Default'
    
    #patterns for finding the phone number
    phone_pattern_1 = r'[\d]?[(]{1}[\d]{3}[)]{1}[\s]?[\d]{3}[-\s]{1}[\d]{4}'
    phone_pattern_2 = r'[+]{1}[\d]{2}[\s]{1}[(]?[\+]?[)]?[\d]{2}[\s]{1}[\d]{4}[\s]{1}[\d]{4}'
    phone_pattern_3 = r'[+]{1}[\d]{2}[\s]{1}[(]?[\d]?[)]?[\d]{3}[\s]{1}[\d]{3}[\s]{1}[\d]{3}'
    phone_pattern_4 = r'[\d]{3}[-\s]{1}[\d]{3}[-\s]{1}[\d]{4}'
    phone_pattern = [phone_pattern_1,phone_pattern_2,phone_pattern_3,phone_pattern_4]


    cnt = 1
    google_result_link = []
    cnt_list = []
    full_name = query.lower()
    name_split = full_name.split()

    output_match_term = []
    output_list_search = []
    output_list_url_no = []
    output_list_line_no = []
    output_list_span_start = []
    output_list_span_end = []
    output_line = []
    output_word = []
    output_list_match_count = []

    entities = []
    labels = []
    model_name = []
    is_correct = []
    position_start = []
    position_end = []
    line_no_list = []
    text_in_the_line = []
    url_no = []
    
    #code to do the web scraping
    for url in search(query, tld="com", num=21, stop=21, pause=2):
        #print(str(cnt)+' '+url)
        try:        
            if url[-4:] == '.pdf' or url.find('-image?') != -1: #If its a pdf or image file it skips and go the next search result
                raise ValueError('It is a pdf or image file')    
            google_result_link.append(url)
            cnt_list.append(cnt)
            if cnt == 21: #If cnt == 21 then the first google page link will be downloaded and data will be extracted
                url = name = query.replace(' ','+')
                url = 'https://www.google.com/search?q='+name

            page = requests.get(url,headers=headers)
            soup = BeautifulSoup(page.text,'html.parser')
            parsed_text = soup.get_text()
            text = parsed_text.split('\n') # Cleaning the data 
            text = list(filter(lambda x: x not in ('','\r'),text))   # Cleaning the data 
            
            data_into_list = []
            try:  
                for line in text:
                    if not line.isspace():
                        if cnt == 21:
                            if line.find('https://') > -1:
                                line = line.replace('https://',' https://')
                        aligned_line = align_sentence(line.strip())
                        splitted_lines_list = re.split(r'\. |\.\[', aligned_line)
                        for i in splitted_lines_list:
                            data_into_list.append(i)
                line_no = 0
                
                # All the scraped data are appended to the "data_into_list" varaible
                # from that list looping through the records and find out the PII by calling each function
                
                for line in data_into_list:
                    
                    # Searching for email matches
                    email_matches = re.finditer(r'\S+@\S+', line)
                    for m in email_matches:
                        match_count = 0  
                        try:
                            for name in name_split:
                                if m.group(0).lower().find(name) >= 0:
                                    match_count += 1 
                        except:
                            match_count = 0 
                        inp_list = ['Email',m.group(0),line,m.start(),m.end(),query,cnt,line_no,match_count]
                        append_list(inp_list) 
                    
                    # Searching for phone matches                    
                    txt_before_and_after = ''
                    for pattern in phone_pattern:
                        for m in re.finditer(pattern,line):
                            match_count = 0
                            try:
                                if line_no >= 4:
                                    txt_before_and_after = data_into_list[line_no-4]+'\t'+data_into_list[line_no-3]+'\t'+data_into_list[line_no-2]+'\t'+data_into_list[line_no-1]+'\t'+data_into_list[line_no]+'\t'+data_into_list[line_no+1]+'\t'+data_into_list[line_no+2]
                                else:
                                    txt_before_and_after = data_into_list[line_no]+'\t'+data_into_list[line_no+1]+'\t'+data_into_list[line_no+2]
                                txt_before_and_after = txt_before_and_after.lower()
                                for name in name_split:
                                    if txt_before_and_after.lower().find(name) >= 0:
                                        match_count += 1 
                            except:
                                match_count = 0
                            inp_list = ['Phone',m.group(0),line,m.start(),m.end(),query,cnt,line_no,match_count]
                            append_list(inp_list) 
                    
                    # Searching for Date_of_Birth matches 
                    pattern_values = dob_pattern(line)  
                    if pattern_values:
                        match_count = 0
                        try:
                            if txt_before_and_after is None:
                                if line_no >= 4:
                                    txt_before_and_after = data_into_list[line_no-4]+'\t'+data_into_list[line_no-3]+'\t'+data_into_list[line_no-2]+'\t'+data_into_list[line_no-1]+'\t'+data_into_list[line_no]+'\t'+data_into_list[line_no+1]+'\t'+data_into_list[line_no+2]
                                else:
                                    txt_before_and_after = data_into_list[line_no]+'\t'+data_into_list[line_no+1]+'\t'+data_into_list[line_no+2]
                                txt_before_and_after = txt_before_and_after.lower()
                            
                            for name in name_split:
                                if txt_before_and_after.lower().find(name) >= 0:
                                    match_count += 1
                        except:
                            match_count = 0
                        inp_list = [pattern_values[0],pattern_values[1],line,pattern_values[2],pattern_values[3],query,cnt,line_no,match_count]
                        append_list(inp_list) 
                    
                    # Searching for Address matches 
                    pattern_values = address_pattern(line)  
                    if pattern_values:
                        match_count = 0
                        try:
                            if txt_before_and_after is None:
                                if line_no >= 4:
                                    txt_before_and_after = data_into_list[line_no-4]+'\t'+data_into_list[line_no-3]+'\t'+data_into_list[line_no-2]+'\t'+data_into_list[line_no-1]+'\t'+data_into_list[line_no]+'\t'+data_into_list[line_no+1]+'\t'+data_into_list[line_no+2]
                                else:
                                    txt_before_and_after = data_into_list[line_no]+'\t'+data_into_list[line_no+1]+'\t'+data_into_list[line_no+2]
                                txt_before_and_after = txt_before_and_after.lower()
                            
                            for name in name_split:
                                if txt_before_and_after.lower().find(name) >= 0:
                                    match_count += 1
                        except:
                            match_count = 0
                        inp_list = [pattern_values[0],pattern_values[1],line,pattern_values[2],pattern_values[3],query,cnt,line_no,match_count]
                        append_list(inp_list) 
                    
                    # Searching for Social media matches only for the 21st link
                    if cnt == 21:
                        social_media_list = []
                        if line.find('.linkedin.com') > -1:
                            social_media_list.append('.linkedin.com')
                        if line.find('https://www.instagram.com') > -1:
                            social_media_list.append('https://www.instagram.com')
                        if line.find('https://www.facebook.com') > -1:
                            social_media_list.append('https://www.facebook.com')
                        if line.find('twitter.com') > -1:
                            social_media_list.append('twitter.com')
                        #print('social_media_list is ',social_media_list)
                        if social_media_list:
                            out_social_med_list = find_social_media_acnt(social_media_list,line) 
                            #print('out_social_med_list is ',out_social_med_list)
                            match_count = 0  
                            try:
                                for name in name_split:
                                    if out_social_med_list[0][0].lower().find(name) >= 0:
                                        match_count += 1 
                            except:
                                match_count = 0 
                            inp_list = [out_social_med_list[0][1],out_social_med_list[0][0],line,'','',query,cnt,line_no,match_count]
                            append_list(inp_list)                          
                    
                    # Searching for Locations 
                    doc = nlp(str(line.strip()))  
        
                    mod_name = 'Spacy'
                    for ent in doc.ents:
                        if ent.label_ == 'GPE':
                            is_correct.append('Y')
                            entities.append(str(ent).strip())
                            labels.append(ent.label_)
                            model_name.append(mod_name)
                            position_start.append(ent.start_char)
                            position_end.append(ent.end_char)
                            line_no_list.append(cnt)
                            text_in_the_line.append(line.strip())
                            url_no.append(cnt)

                    line_no += 1
                
            except Exception as e:
                print(e)
                print('Error: '+url)
            cnt += 1
        except ValueError as f:
            print(f)
            print('Error1: '+url)   
            cnt += 1   
        except Exception as e:
            cnt += 1
            print(e)
            print('Error1: '+url)
    
    try:
        df_person_gpe = pd.DataFrame({'Is_correct':is_correct,'Entities':entities,'Labels':labels,'Model_name':model_name,
                                        'Position_start':position_start,'Position_end':position_end,'Line_no':line_no_list,
                                        'Text_in_the_line':text_in_the_line,'URL_No.':url_no})
        df_person_gpe_unique = df_person_gpe[['Entities','URL_No.']]
        df_person_gpe_unique = df_person_gpe_unique.drop_duplicates()
        df_person_gpe_count = df_person_gpe_unique.groupby(['Entities'])['Entities'].count().reset_index(name='count').sort_values(by='count',ascending=False)
        df_person_gpe_max = df_person_gpe_count.query('count == count.max()')

        inp_list = ['Location',df_person_gpe_max.iloc[0,0],'','','',query,'','',df_person_gpe_max.iloc[0,1]]
        append_list(inp_list) 
        

        df = pd.DataFrame({'Match term':output_match_term,'Match Word/Text':output_word,'Line':output_line,
                            'Span start':output_list_span_start,'Span end':output_list_span_end,
                            'output_list_search':output_list_search,'output_list_url_no':output_list_url_no,
                            'output_list_line_no':output_list_line_no,'Match Count':output_list_match_count})
        

        rslt_df = df[df['Match Count'] > 0]
        rslt_df = rslt_df.sort_values(['Match Count'], ascending=[0])
        rslt_df = rslt_df.drop_duplicates( subset = ['Match term', 'Match Word/Text'],  keep = 'last').reset_index(drop = True)
        rslt_df = rslt_df[['Match term', 'Match Word/Text']]

        dictionary = {}

        for index,row in rslt_df.iterrows():
            #print(row['Match term'],' ',row['Match Word/Text'])
            if row['Match term'] in dictionary:
                dictionary[row['Match term']].append(row['Match Word/Text'])
            else:
                dictionary[row['Match term']] = [row['Match Word/Text']]
        #print('dictionary ',dictionary)

        pii_attributes = list(dictionary.keys())


        def calculate_privacy_score(willingness_measure, resolution_power, beta_coefficient):
            from math import exp
            privacy_score = 1 / exp(beta_coefficient * (1 - willingness_measure) * resolution_power)
            return privacy_score

        def calculate_overall_risk_score(pii_attributes, weights, willingness_measures, resolution_powers,
                                         beta_coefficients):
            overall_risk_score = 0
            for attribute in pii_attributes:
                weight = weights.get(attribute, 0)
                willingness_measure = willingness_measures.get(attribute, 0)
                resolution_power = resolution_powers.get(attribute, 0)
                beta_coefficient = beta_coefficients.get(attribute, 1)
                privacy_score = calculate_privacy_score(willingness_measure, resolution_power, beta_coefficient)
                overall_risk_score += weight * privacy_score
            return overall_risk_score

        # extracted PII data
        """
        pii_attributes = set()
        pii_attributes.update(dictionary.keys())
        pii_attributes = list(pii_attributes) 
        """

        #pii_attributes = list(dictionary.keys())


            # Define weights, willingness_measures, resolution_powers, beta_coefficients for PII attributes
            # These should be replaced with your actual data based on the documentation provided
        weights = {
                'Name': 1,
                'Address': 1,
                'Location':1,
                'Gender': 1,
                'Employer': 2,
                'DoB': 2,
                'Education': 1,
                'Birth Place': 2,
                'Personal Cell': 0.5,
                'Email': 0.1,
                'Business Phone': 0.1,
                'Facebook Account': 1,
                'Twitter Account': 0.1,
                'Instagram Account': 0.1,
                'DDL': 2,
                'Passport #': 2,
                'Credit Card': 2,
                'SSN': 10
        }
        willingness_measures = {
                'Name': 1.0,  # Name is often publicly shared.
                'Address': 0.1,
                'Location':0.1, #Address is less commonly shared due to privacy concerns.
                'Birth Place': 0.2,
                'DoB': 0.83,  # Date of Birth may be shared on social platforms.
                'Personal Cell': 0.16,  # Personal cell numbers are usually shared with reservations.
                'Gender': 0.98,  # Gender is often shared on social profiles.
                'Employer': 0.5,  # Details about one's employer can be commonly found on professional networks.
                'Education': 0.8,  # Education details are often listed on social and professional networks.
                'Email': 0.7,  # Email addresses are frequently shared for contact purposes.
                'Business Phone': 0.4,
                # Business phone numbers are often available but less willingly shared than emails.
                'Facebook Account': 0.9,  # Social media accounts are typically public.
                'Twitter Account': 0.9,
                'Instagram Account': 0.9,
                'DDL': 0.2,  # Driver's license details are sensitive and less frequently shared.
                'Passport #': 0.05,  # Passport numbers are highly sensitive and rarely shared.
                'Credit Card': 0.02,
                # Credit card details are highly sensitive and shared only in trusted transactions.
                'SSN': 0.01  # Social Security Numbers are among the most sensitive PII and rarely shared.
        }

        resolution_powers = {
            'Name': 0.1,  # Common names have lower resolution power.
            'Address': 0.3,   'Location':0.1,                 # Addresses can be shared by multiple individuals (e.g., families).
            'DoB': 0.7,  # Dates of birth can be unique but may also be shared by others.
            'Personal Cell': 0.9,  # Personal cell numbers are typically unique to individuals.
            'Email': 0.95,  # Email addresses are unique identifiers.
            'Business Phone': 0.4,  # Business phone numbers might be shared by multiple employees.
            'Facebook Account': 0.8,  # Social media handles are often unique.
            'Twitter Account': 0.8,
            'Instagram Account': 0.8,
            'DDL': 1.0,  # Driver's license numbers are unique identifiers.
            'Passport #': 1.0,  # Passport numbers are unique to individuals.
            'Credit Card': 1.0,  # Credit card numbers are unique identifiers.
            'SSN': 1.0,  # Social Security Numbers are unique to each individual.
            'Gender': 0.1,  # Gender itself is not a unique identifier.
            'Employer': 0.2,  # Many individuals can have the same employer.
            'Education': 0.3,  # Education information may not uniquely identify an individual.
            'Birth Place': 0.5  # Birth places could be shared by many individuals, thus lower than 1.
        }
        beta_coefficients = {
            'Name': 1,  # Direct influence of willingness and resolution.
            'Address': 1, 'Location':0.1,
            'DoB': 1,
            'Personal Cell': 1,
            'Email': 1,
            'Business Phone': 1,
            'Facebook Account': 1,
            'Twitter Account': 1,
            'Instagram Account': 1,
            'DDL': 1,
            'Passport #': 1,
            'Credit Card': 1,
            'SSN': 1,
            'Gender': 1,
            'Employer': 1,
            'Education': 1,
            'Birth Place': 1
            # Additional attributes would also have beta coefficients set here.
        }

        # Calculating the overall risk score
        overall_risk_score = calculate_overall_risk_score(
            pii_attributes,
            weights,
            willingness_measures,
            resolution_powers,
            beta_coefficients)

        if overall_risk_score <= 2.74:
            risk_level = 'Very Low'
        elif 2.74 < overall_risk_score <= 5.48:
            risk_level = 'Low'
        elif 5.48 < overall_risk_score <= 6.87:
            risk_level = 'Medium'
        elif 6.87 < overall_risk_score <= 12.25:
            risk_level = 'High'
        else:
            risk_level = 'Very High'

        # Creating the JSON response with the risk score
      # json_response = {
      #     'pii_data': pii_attributes,
      #     'risk_score': overall_risk_score,
      #     'risk_level': risk_level
      # }
        dictionary['risk_score'] = overall_risk_score
        dictionary['risk_level'] = risk_level




        json_object = json.dumps(dictionary, indent = 2)

        return json_object

    except Exception as e:
            print('Error2: '+url)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run(debug=False)#,port=2000