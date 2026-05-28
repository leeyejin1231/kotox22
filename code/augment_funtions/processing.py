from pickletools import read_uint1
import hgtk
import random
import json
import re
from G2P.KoG2Padvanced import KoG2Padvanced

DEFAULT_COMPOSE_CODE = "ᴥ"

class Processing:
    def __init__(self):
        with open("./rules/replace.json", "r") as f:
            self.replace_dict = json.load(f)
        self.last_replace_map = {}
        for i in ["ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅇ"]:
            self.last_replace_map[i] = []
        for key in self.replace_dict["real_sound_map"]:
            self.last_replace_map[self.replace_dict["real_sound_map"][key]].append(key)
    
    # 1-A replacement
    ## initial sound -> soft sound, strong sound replacement
    def first_power_replace(self, input_span):
        result = []
        for char in list(input_span):
            if hgtk.checker.is_hangul(char):
                cho, jung, jong = hgtk.letter.decompose(char)
                if jung == '' or cho == '':
                    continue
                if cho in self.replace_dict["power_replace_map"]:
                    candidate = random.choice(self.replace_dict["power_replace_map"][cho])
                    result.append(hgtk.letter.compose(candidate,jung,jong))
                else:
                    result.append(hgtk.letter.compose(cho,jung,jong))
            else:
                result.append(char)
        return ''.join(result) 

    ## initial sound -> soft sound, strong sound replacement
    def reverse_first_power_replace(self, input_span):
        result = []
        for char in list(input_span):
            if hgtk.checker.is_hangul(char):
                cho, jung, jong = hgtk.letter.decompose(char)
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                if cho in self.replace_dict["reverse_power_replace_map"]:
                    result.append(hgtk.letter.compose(random.choice(self.replace_dict["reverse_power_replace_map"][cho]), jung, jong))
                else:
                    result.append(hgtk.letter.compose(cho, jung, jong))
            else:
                result.append(char)
        return ''.join(result)

    ## vowel replacement
    def vowel_replace(self, input_span):
        result = []
        for char in list(input_span):
            if hgtk.checker.is_hangul(char):
                cho, jung, jong = hgtk.letter.decompose(char)
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                if jung in self.replace_dict["vowel_replace_map"]:
                    result.append(hgtk.letter.compose(cho, random.choice(self.replace_dict["vowel_replace_map"][jung]), jong))
                else:
                    result.append(hgtk.letter.compose(cho, jung, jong))
            else:
                result.append(char)
        return ''.join(result)
    
    ## final consonant replacement
    def last_replace(self, input_span):
        result = []
        for char in list(input_span):
            if hgtk.checker.is_hangul(char):
                cho, jung, jong = hgtk.letter.decompose(char)
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                if jong != '' and jong in self.replace_dict["real_sound_map"]:
                    new_jong = random.choice(self.last_replace_map[self.replace_dict["real_sound_map"][jong]])
                    result.append(hgtk.letter.compose(cho, jung, new_jong))
                else:
                    result.append(hgtk.letter.compose(cho, jung, jong))
            else:
                result.append(char)
        return ''.join(result)

    ## phonetic variation
    def sound_like_replace(self, input_span):
        # finditer to get the position of the matched part accurately
        matches = list(re.finditer(r'[가-힣]+', input_span))
        if matches:
            # change from the end to avoid index confusion
            result_text = input_span
            for match in reversed(matches):
                start, end = match.span()
                matched_text = match.group()
                # print(f"Matched: {matched_text} at {start}-{end}")
                converted_korean = KoG2Padvanced(matched_text)
                result_text = result_text[:start] + converted_korean + result_text[end:]
            return result_text
        else:
            return input_span

    # 1-C liaison
    ## liaison
    def continue_sound(self, input_span):
        result = []
        chars = list(input_span)
        flag = False
        
        for i, char in enumerate(chars):
            if hgtk.checker.is_hangul(char):
                cho, jung, jong = hgtk.letter.decompose(char)
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                
                if flag:
                    flag = False
                    continue
                
                # Check if there's a next character and if current character has final consonant
                if i < len(chars) - 1 and jong != '' and hgtk.checker.is_hangul(chars[i + 1]):
                    next_cho, next_jung, next_jong = hgtk.letter.decompose(chars[i + 1])
                    if next_jung == '' or next_cho == '':
                        result.append(char)
                        continue

                    # Create the combination pattern
                    combination = jong + 'ᴥ' + next_cho
                    
                    if combination in self.replace_dict["continue_sound_map"]:
                        # Apply continue sound transformation
                        new_combination = self.replace_dict["continue_sound_map"][combination]
                        # print(f"new_next_cho: {cho}, next_jung: {jung}, next_jong: {jong}")
                        
                        new_cur_jong = new_combination.split('ᴥ')[0]
                        new_next_cho = new_combination.split('ᴥ')[1]

                        result.append(hgtk.letter.compose(cho, jung, new_cur_jong))
                        result.append(hgtk.letter.compose(new_next_cho, next_jung, next_jong))
                        
                        # Skip the next character as it's already processed
                        flag = True
                    else:
                        result.append(char)
                else:
                    result.append(char)
            else:
                result.append(char)
        
        if ''.join(result) == input_span:
            return self.reverse_continue_sound(input_span)

        return ''.join(result)

    ## reverse liaison
    def reverse_continue_sound(self, input_span):
        result = []
        chars = list(input_span)
        
        for i, char in enumerate(chars):
            if chars[i] is None:  # Skip already processed characters
                continue
                
            if hgtk.checker.is_hangul(char):
                cho, jung, jong = hgtk.letter.decompose(char)
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                
                # Check if there's a next character
                if i < len(chars) - 1 and chars[i + 1] is not None and hgtk.checker.is_hangul(chars[i + 1]):
                    next_cho, next_jung, next_jong = hgtk.letter.decompose(chars[i + 1])
                    if next_jung == '' or next_cho == '':
                        result.append(char)
                        continue
                
                    
                    # Create the combination pattern for reverse continue sound
                    combination = cho + 'ᴥ' + next_cho
                    
                    # Check with batchim map first
                    if hgtk.checker.has_batchim(char) and combination in self.replace_dict["reverse_continue_sound_with_batchim_map"]:
                        candidate = self.replace_dict["reverse_continue_sound_with_batchim_map"][combination]
                        new_next_cho = 'ㅇ'
                        new_jong = candidate.split('ᴥ')[0]
                        new_next_cho = candidate.split('ᴥ')[1]
                        result.append(hgtk.letter.compose(cho, jung, new_jong))
                        result.append(hgtk.letter.compose(new_next_cho, next_jung, next_jong))
                        
                        # Skip the next character as it's already processed
                        chars[i + 1] = None
                    # Check without batchim map
                    elif not hgtk.checker.has_batchim(char) and combination in self.replace_dict["reverse_continue_sound_without_batchim_map"]:
                        candidate = self.replace_dict["reverse_continue_sound_without_batchim_map"][combination]
                        new_next_cho = 'ㅇ'
                        new_jong = candidate.split('ᴥ')[0]
                        new_next_cho = candidate.split('ᴥ')[1]
                        result.append(hgtk.letter.compose(cho, jung, new_jong))
                        result.append(hgtk.letter.compose(new_next_cho, next_jung, next_jong))
                        
                        # Skip the next character as it's already processed
                        chars[i + 1] = None
                    else:
                        result.append(char)
                else:
                    result.append(char)
            else:
                result.append(char)
        
        return ''.join(result)


if __name__ == "__main__":
    processing = Processing()
    
    print("=== Comprehensive test of Korean processing module ===\n")