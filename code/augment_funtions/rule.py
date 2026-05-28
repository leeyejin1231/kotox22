import os
import openai
import random
import json
import hgtk
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

class SyntaticObfuscation:
    def __init__(self):\
        pass
    
    def spacing(self, text_list: str) -> str:
        """
        4-A. spacing
        """
        option = random.choice([0, 1])
        if option == 0:
            result = ""
            for span in text_list:
                result += span['span'][-1]
            return result
        else:
            result_list = []
            applied_index = []
            for i in range(len(text_list)):
                word = text_list[i]['span'][-1]
                applied_rule = text_list[i]['applied_rule']
                # insert spacing only if the word length is 2 or more, and array obfuscation is not applied
                if len(word) > 1 and '11' not in applied_rule:
                    # insert position is randomly selected from 1 ~ len(word)-1
                    insert_pos = random.randint(1, len(word)-1)
                    word = word[:insert_pos] + " " + word[insert_pos:]
                    result_list.append(word)
                    applied_index.append(i)
                else:
                    result_list.append("")
            
            # if less than 40%, just insert spacing
            if len(applied_index) < int(len(text_list)*0.4):
                result = ""
                for span in text_list:
                    result += span['span'][-1]
                return result
            else:
                selected_span = random.sample(applied_index, int(len(text_list)*0.4))
                result = ""
                for i in range(len(result_list)):
                    if i in selected_span:
                        result += result_list[i] + " "
                    else:
                        result += text_list[i]['span'][-1] + " "
                
                return result.rstrip()
                

    def change_array(self, text: str) -> str:
        """
        4-B. array obfuscation
        """
        spans = text.split(" ")
        obfuscated = [self.obfuscate_span(span) for span in spans]
        output = " ".join(obfuscated)
        return output

    def obfuscate_span(self, span: str) -> str:
        if len(span) <= 2:
            return span
        chars = list(span)
        if len(span) == 3:
            middle = chars[1]
            if random.random() < 0.7:
                chars[1], chars[2] = chars[2], chars[1]
            return "".join(chars)
        middle = chars[1:-1]
        if len(middle) > 1:
            shuffled = middle[:]
            for _ in range(3):
                random.shuffle(shuffled)
                if shuffled != middle:
                    break
            chars = [chars[0]] + shuffled + [chars[-1]]
        return "".join(chars)


# 3. iconic replacement
class IconicObfuscation:
    def __init__(self):
        with open("./rules/iconic_dictionary.json", "r") as f:
            self.iconic_dict = json.load(f)
            # self.okt = Okt()

    def yamin_swap(self, text: str) -> str:
        for key in self.iconic_dict['yamin_dict'].keys():
            if key in text:
                text = text.replace(key, random.choice(self.iconic_dict["yamin_dict"][key]))

        return text

    def gana_swap(self, text: str) -> str:
        text_list = list(text)
        for i in range(len(text_list)):
            if text_list[i] in self.iconic_dict["gana_dict"].keys():
                text_list[i] = random.choice(self.iconic_dict["gana_dict"][text_list[i]])
        return "".join(text_list)

    def consonant_swap(self, text: str) -> str:
        result = list(text)
        for i in range(len((text))):
            if hgtk.checker.is_hangul(result[i]):
                cho, jung, jong = hgtk.letter.decompose(result[i])
                if jung+jong in self.iconic_dict["vowel_dict"].keys():
                    jung = random.choice(self.iconic_dict["vowel_dict"][jung+jong])
                    jong == ""
                elif jong == "" and jung in self.iconic_dict["vowel_dict"].keys():
                    jung = random.choice(self.iconic_dict["vowel_dict"][jung])
                elif jung not in ['ㅗ','ㅛ','ㅜ','ㅠ','ㅡ','ㅚ','ㅙ','ㅞ','ㅟ','ㅝ','ㅘ'] and jong == "" and cho in self.iconic_dict["consonant_dict"].keys():
                    cho = random.choice(self.iconic_dict["consonant_dict"][cho])
                try:
                    result[i] = hgtk.letter.compose(cho, jung, jong)
                except:
                    result[i] = cho + jung + jong
            else:
                pass

        return "".join(result)

    def rotation_swap(self, text: str) -> str:
        for key in self.iconic_dict["rotation_dict"].keys():
            if key in text:
                text = text.replace(key, random.choice(self.iconic_dict["rotation_dict"][key]))
        return text

    def rotation_180_swap(self, text: str) -> str:
        for key in self.iconic_dict["rotation_180_dict"].keys():
            if key in text:
                text = text.replace(key, random.choice(self.iconic_dict["rotation_180_dict"][key]))
        return text

    def compression_swap(self, text: str) -> str:
        for key in self.iconic_dict["compression_dict"].keys():
            if key in text:
                text = text.replace(key, random.choice(self.iconic_dict["compression_dict"][key]))
        return text


### 3. transliterational approach
class TransliterationalObfuscation:
    def __init__(self):
        with open("./rules/transliterational_dictionary.json", "r") as f:
            self.transliterational_dict = json.load(f)  
            self.client = openai.OpenAI(api_key=API_KEY)     

    def iconic_swap(self, text: str) -> str:
        with open("./rules/latin_prompt.txt", "r") as file:
            prompt = file.read()
        
        messages = [
            {"role": "system", "content": prompt}, 
            {"role": "user", "content": text}
            ]
        
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
        )
        
        try:
            response = response.choices[0].message.content
            response.replace("```json", "").replace("```", "")
            response = json.loads(response)
        except Exception as e:
            print(f"error: {e}")
            return text
        
        return response["output"]

    def foreign_iconic_swap(self, text: str) -> str:
        with open("./rules/korean_prompt.txt", "r") as file:
            prompt = file.read()
        
        messages = [
            {"role": "system", "content": prompt}, 
            {"role": "user", "content": text}
            ]
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
        )

        try:
            response = response.choices[0].message.content
            response.replace("```json", "").replace("```", "")
            response = json.loads(response)
        except Exception as e:
            print(f"error: {e}")
            return text
        
        return response["output"]

    def meaning_swap(self, text: str) -> str:
        for key in self.transliterational_dict["meaning_dict"].keys():
            if key in text:
                text = text.replace(key, random.choice(self.transliterational_dict["meaning_dict"][key]))
        return text


# 6. pragmatic approach
# 6-A. expression addition
class SymbolAddition:
    def __init__(self):
        # heart related symbols
        self.hearts = ['♡', '♥', '♤', '♧']
        # star and geometric symbols
        self.stars = ['★', '☆', '✦', '✧', '✩', '✪']
        # circular symbols
        self.circles = ['○', '●', '◎', '◯', '◈', '◉', '◊']
        # geometric shapes
        self.shapes = ['◇', '◆', '□', '■', '▲', '△', '▼', '▽']
        # brackets and quotation marks
        self.brackets = ['【', '】', '《', '》', '「', '」', '『', '』', '∥', '〃']
        # punctuation and special characters
        self.punctuation = ['‥', '…', '、', '。', '．', '¿', '？', "!", "1"]
        # emotion related symbols
        self.emotions = ['ε♡з', 'ε♥з', 'T^T', '∏-∏', '≥ㅇ≤', '≥ㅅ≤', '≥ㅂ≤', '≥ㅁ≤', '≥ㅃ≤']
        # decorative symbols
        self.decorations = ['━', '─', '┃', '┗', '┣', '┓', '┫', '┛', '┻', '┳']
        # special characters
        self.special = ['¸', 'º', '°', '˛', '˚', '¯', '´', '`', '¨', 'ˆ', '˜', '˙']

    def add_hearts(self, text: str, probability: float = 0.3) -> str:

        words = text.split()
        result = []
        
        for word in words:
            result.append(word)
            
            if random.random() < probability:
                heart = random.choice(self.hearts)
                result.append(heart)
            
            if random.random() < probability * 0.5:
                heart = random.choice(self.hearts)
                result.append(heart)
        
        return ' '.join(result)

    def add_stars(self, text: str, probability: float = 0.2) -> str:

        words = text.split()
        result = []
        
        for word in words:
            if random.random() < probability:
                star = random.choice(self.stars)
                result.append(star)
            
            result.append(word)
            
            if random.random() < probability:
                star = random.choice(self.stars)
                result.append(star)
        
        return ' '.join(result)

    def add_circles(self, text: str, probability: float = 0.15) -> str:

        words = text.split()
        result = []
        
        for word in words:
            if random.random() < probability:
                circle = random.choice(self.circles)
                result.append(f"{circle}{word}{circle}")
            else:
                result.append(word)
        
        return ' '.join(result)

    def add_brackets(self, text: str, probability: float = 0.25) -> str:

        words = text.split()
        result = []
        
        for word in words:
            if random.random() < probability:
                bracket_pair = random.choice([
                    ('【', '】'), ('《', '》'), ('「', '」'), 
                    ('『', '』'), ('∥', '∥'), ('〃', '〃')
                ])
                result.append(f"{bracket_pair[0]}{word}{bracket_pair[1]}")
            else:
                result.append(word)
        
        return ' '.join(result)

    def add_punctuation(self, text: str, probability: float = 0.2) -> str:
        result = text

        # add special punctuation at the end of the sentence
        if random.random() < probability:
            punct = random.choice(self.punctuation)
            result += punct

        # add dots in the middle of the sentence
        if random.random() < probability * 0.7:
            dots = random.choice(['‥', '…'])
            result = result.replace(' ', f' {dots} ', 1)

        # add special punctuation in the middle of the word
        words = result.split()
        new_words = []
        for word in words:
            if len(word) > 1 and random.random() < probability:
                # select the position in the middle of the word
                insert_pos = random.randint(1, len(word)-1)
                punct = random.choice(self.punctuation)
                # add special punctuation in the middle of the word
                new_word = word[:insert_pos] + punct + word[insert_pos:]
                new_words.append(new_word)
            else:
                new_words.append(word)
        result = ' '.join(new_words)

        return result

    def add_emotions(self, text: str, probability: float = 0.15) -> str:

        words = text.split()
        result = []
        
        for word in words:
            result.append(word)
            
            if random.random() < probability:
                emotion = random.choice(self.emotions)
                result.append(emotion)
        
        return ' '.join(result)

    def add_decorations(self, text: str, probability: float = 0.1) -> str:

        result = text
        
        if random.random() < probability:
            decoration = random.choice(self.decorations)
            result = f"{decoration} {result} {decoration}"
        
        return result

    def add_special_chars(self, text: str, probability: float = 0.1) -> str:

        words = text.split()
        result = []
        
        for word in words:
            if random.random() < probability:
                special = random.choice(self.special)
                if random.random() < 0.5:
                    result.append(f"{word}{special}")
                else:
                    result.append(f"{special}{word}")
            else:
                result.append(word)
        
        return ' '.join(result)

    def comprehensive_symbol_addition(self, text: str) -> str:

        result = text
        
        result = self.add_hearts(result, 0.2)
        result = self.add_stars(result, 0.15)
        result = self.add_circles(result, 0.1)
        result = self.add_brackets(result, 0.15)
        result = self.add_punctuation(result, 0.2)
        result = self.add_emotions(result, 0.1)
        result = self.add_decorations(result, 0.05)
        result = self.add_special_chars(result, 0.05)
        
        result = ' '.join(result.split())
        
        return result


if __name__ == "__main__":
    symbol_addition = SymbolAddition()
    print(symbol_addition.comprehensive_symbol_addition("Hello, world!"))
