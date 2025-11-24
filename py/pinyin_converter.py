"""
Chinese to Pinyin Converter Module
Converts Chinese characters to pinyin without tone marks for TTS processing
"""


class ChinesePinyinConverter:
    """Convert Chinese characters to pinyin without tone marks"""

    def __init__(self):
        """Initialize pinyin converter"""
        try:
            from pypinyin import Style, lazy_pinyin

            self.lazy_pinyin = lazy_pinyin
            self.Style = Style
            self._available = True
        except ImportError:
            print("Warning: pypinyin not installed. Chinese support disabled.")
            self._available = False

        # Pronunciation conversion mapping for specific pinyin syllables
        self.pronunciation_map = {
            "qing": "tsing",
            "xing": "sing",
            "jing": "tsing",
            "qin": "tsin",
            "xin": "sin",
            "jin": "tsin",
            "qiong": "tsiong",
            "xiong": "siong",
            "jiong": "tsiong",
            "qia": "tsia",
            "xia": "sia",
            "jia": "tsia",
            "qie": "tsie",
            "xie": "sie",
            "jie": "tsie",
            "qiu": "tsiu",
            "xiu": "siu",
            "jiu": "tsiu",
        }

    def is_chinese_char(self, char: str) -> bool:
        """Check if a character is Chinese"""
        return "\u4e00" <= char <= "\u9fff"

    def chinese_to_pinyin(self, text: str) -> str:
        """Convert Chinese characters to pinyin without spaces"""
        if not self._available:
            return text

        result = []
        for char in text:
            if self.is_chinese_char(char):
                # Use Style.NORMAL to get pinyin without tone marks
                pinyin_list = self.lazy_pinyin(char, style=self.Style.NORMAL)
                if pinyin_list:
                    result.append(pinyin_list[0])
            else:
                # Keep English, numbers, punctuation as is
                result.append(char)
        return "".join(result)

    def chinese_to_pinyin_with_spaces(self, text: str) -> str:
        """Convert Chinese characters to pinyin with proper spacing"""
        if not self._available:
            return text

        # Process the text and identify Chinese vs non-Chinese segments
        segments = []
        current_segment = ""
        current_is_chinese = False

        for char in text:
            is_chinese = self.is_chinese_char(char)

            if not current_segment:
                current_segment = char
                current_is_chinese = is_chinese
            elif is_chinese == current_is_chinese:
                current_segment += char
            else:
                segments.append((current_segment, current_is_chinese))
                current_segment = char
                current_is_chinese = is_chinese

        if current_segment:
            segments.append((current_segment, current_is_chinese))

        # Convert each segment
        result_parts = []
        for segment, is_chinese in segments:
            if is_chinese:
                # Convert Chinese characters to pinyin with spaces
                pinyin_list = self.lazy_pinyin(segment, style=self.Style.NORMAL)
                result_parts.append(" ".join(pinyin_list))
            else:
                # Keep non-Chinese text as is
                result_parts.append(segment)

        # Join segments with spaces where appropriate
        result = ""
        for i, part in enumerate(result_parts):
            if i > 0:
                # Add space between segments if both contain alphabetic characters
                prev_part = result_parts[i - 1]
                if part and prev_part and part[0].isalpha() and prev_part[-1].isalpha():
                    result += " "
            result += part

        return result

    def detect_chinese_content(self, text: str) -> bool:
        """Detect if text contains Chinese characters"""
        return any(self.is_chinese_char(char) for char in text)

    def convert_pronunciation(self, pinyin: str) -> str:
        """Convert pinyin pronunciation using the pronunciation map"""
        return self.pronunciation_map.get(pinyin, pinyin)

    def chinese_to_pinyin_with_pronunciation(self, text: str) -> str:
        """Convert Chinese characters to pinyin with pronunciation conversion"""
        if not self._available:
            return text

        result = []
        for char in text:
            if self.is_chinese_char(char):
                # Get pinyin without tone marks
                pinyin_list = self.lazy_pinyin(char, style=self.Style.NORMAL)
                if pinyin_list:
                    # Apply pronunciation conversion
                    converted_pinyin = self.convert_pronunciation(pinyin_list[0])
                    result.append(converted_pinyin)
            else:
                # Keep English, numbers, punctuation as is
                result.append(char)
        return "".join(result)

    def chinese_to_pinyin_with_spaces_and_pronunciation(self, text: str) -> str:
        """Convert Chinese characters to pinyin with spaces and pronunciation conversion"""
        if not self._available:
            return text

        # Process the text and identify Chinese vs non-Chinese segments
        segments = []
        current_segment = ""
        current_is_chinese = False

        for char in text:
            is_chinese = self.is_chinese_char(char)

            if not current_segment:
                current_segment = char
                current_is_chinese = is_chinese
            elif is_chinese == current_is_chinese:
                current_segment += char
            else:
                segments.append((current_segment, current_is_chinese))
                current_segment = char
                current_is_chinese = is_chinese

        if current_segment:
            segments.append((current_segment, current_is_chinese))

        # Convert each segment
        result_parts = []
        for segment, is_chinese in segments:
            if is_chinese:
                # Convert Chinese characters to pinyin with pronunciation conversion
                pinyin_list = self.lazy_pinyin(segment, style=self.Style.NORMAL)
                converted_pinyin = [self.convert_pronunciation(p) for p in pinyin_list]
                result_parts.append(" ".join(converted_pinyin))
            else:
                # Keep non-Chinese text as is
                result_parts.append(segment)

        # Join segments with spaces where appropriate
        result = ""
        for i, part in enumerate(result_parts):
            if i > 0:
                # Add space between segments if both contain alphabetic characters
                prev_part = result_parts[i - 1]
                if part and prev_part and part[0].isalpha() and prev_part[-1].isalpha():
                    result += " "
            result += part

        return result

    def get_conversion_info(self, text: str) -> dict:
        """Get information about the conversion process"""
        chinese_chars = [char for char in text if self.is_chinese_char(char)]
        return {
            "has_chinese": len(chinese_chars) > 0,
            "chinese_count": len(chinese_chars),
            "total_length": len(text),
            "chinese_percentage": len(chinese_chars) / len(text) * 100 if text else 0,
            "converter_available": self._available,
            "pronunciation_map_size": len(self.pronunciation_map),
        }


# Test function for development
def test_pinyin_converter():
    """Test the pinyin converter with various inputs"""
    converter = ChinesePinyinConverter()

    test_cases = [
        ("你好世界", "ni hao shi jie"),
        ("Hello world", "Hello world"),
        ("Hello 你好 world 世界", "Hello ni hao world shi jie"),
        ("今天天气很好", "jin tian tian qi hen hao"),
        ("123 你好 456", "123 ni hao 456"),
        ("", ""),
        ("A你好B", "A ni hao B"),
    ]

    print("Testing Chinese Pinyin Converter:")
    print("=" * 50)

    for input_text, expected in test_cases:
        result = converter.chinese_to_pinyin_with_spaces(input_text)
        info = converter.get_conversion_info(input_text)

        print(f"Input:    '{input_text}'")
        print(f"Expected: '{expected}'")
        print(f"Result:   '{result}'")
        print(f"Match:     {result == expected}")
        print(f"Info:      {info}")
        print("-" * 30)

    # Test pronunciation conversion
    print("\nTesting Pronunciation Conversion:")
    print("=" * 50)

    pronunciation_test_cases = [
        ("请", "qing", "tsing"),
        ("星", "xing", "sing"),
        ("静", "jing", "tsing"),
        ("亲", "qin", "tsin"),
        ("新", "xin", "sin"),
        ("今", "jin", "tsin"),
        ("请安静", "qing an jing", "tsing an tsing"),
        ("星星很新", "xing xing hen xin", "sing sing hen sin"),
    ]

    for input_text, original_pinyin, expected_converted in pronunciation_test_cases:
        # Test single character conversion
        if len(input_text) == 1:
            converted = converter.chinese_to_pinyin_with_pronunciation(input_text)
            print(f"Input: '{input_text}' -> '{original_pinyin}' -> '{converted}' (Expected: '{expected_converted}')")
        else:
            # Test multi-character conversion
            converted = converter.chinese_to_pinyin_with_spaces_and_pronunciation(input_text)
            print(f"Input: '{input_text}' -> '{original_pinyin}' -> '{converted}' (Expected: '{expected_converted}')")
        print("-" * 30)


if __name__ == "__main__":
    test_pinyin_converter()
