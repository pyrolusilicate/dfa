import graphviz

class DateDFA:
    # Определяем состояния для удобства
    S_START = 'START'
    S_DAY = 'DAY'
    S_SEP1 = 'SEP1'
    S_MONTH_NUM = 'MONTH_NUM'
    S_MONTH_WORD = 'MONTH_WORD'
    S_SEP2 = 'SEP2'
    S_YEAR = 'YEAR'

    def __init__(self):
        self.reset()
        self.found_dates = []

    def reset(self):
        self.state = self.S_START
        self.buffer_day = ""
        self.buffer_month = ""
        self.buffer_year = ""
        # Разделитель помогает понять, в каком мы формате (точки или пробелы)
        self.current_sep = "" 

    def is_rus_letter(self, char):
        return 'а' <= char.lower() <= 'я'

    def process_text(self, text):
        self.found_dates = []
        self.reset()
        
        # Добавляем пробел в конец, чтобы гарантированно завершить обработку года,
        # если текст заканчивается цифрой
        text += " " 

        for char in text:
            self.step(char)
        
        return self.found_dates

    def step(self, char):
        # 1. Состояние: Ожидание начала (День)
        if self.state == self.S_START:
            if char.isdigit():
                self.buffer_day += char
                self.state = self.S_DAY
            # Иначе просто пропускаем мусорные символы

        # 2. Состояние: Считывание Дня
        elif self.state == self.S_DAY:
            if char.isdigit():
                self.buffer_day += char
            elif char in ['.', ' ']:
                self.current_sep = char # Запоминаем разделитель
                self.state = self.S_SEP1
            else:
                self.reset() # Ошибка структуры, сброс

        # 3. Состояние: Разделитель 1 (между Днем и Месяцем)
        elif self.state == self.S_SEP1:
            if char.isdigit() and self.current_sep == '.':
                self.buffer_month += char
                self.state = self.S_MONTH_NUM
            elif self.is_rus_letter(char) and self.current_sep == ' ':
                self.buffer_month += char
                self.state = self.S_MONTH_WORD
            else:
                self.reset() # Несоответствие формата (например "12.декабря")

        # 4. Состояние: Месяц числовой (например "01")
        elif self.state == self.S_MONTH_NUM:
            if char.isdigit():
                self.buffer_month += char
            elif char == '.':
                self.state = self.S_SEP2
            else:
                self.reset()

        # 5. Состояние: Месяц словесный (например "декабря")
        elif self.state == self.S_MONTH_WORD:
            if self.is_rus_letter(char):
                self.buffer_month += char
            elif char == ' ':
                self.state = self.S_SEP2
            else:
                self.reset()

        # 6. Состояние: Разделитель 2 (между Месяцем и Годом)
        elif self.state == self.S_SEP2:
            if char.isdigit():
                self.buffer_year += char
                self.state = self.S_YEAR
            else:
                self.reset()

        # 7. Состояние: Год
        elif self.state == self.S_YEAR:
            if char.isdigit():
                self.buffer_year += char
            else:
                # Если встретили не цифру, значит год закончился.
                # Проверяем валидность (год должен быть 4 цифры, для простоты)
                if len(self.buffer_year) == 4:
                    self.save_date()
                
                # Важный момент: текущий символ может быть началом новой даты
                # Поэтому мы делаем reset, но пробуем обработать символ снова в состоянии START
                self.reset()
                if char.isdigit():
                    self.step(char)

    def save_date(self):
        # Формируем выход в формате, требуемом в задании: [День, Месяц, Год]
        # Приводим типы (день и год - числа, месяц - по ситуации)
        try:
            d = int(self.buffer_day)
            y = int(self.buffer_year)
            # Месяц оставляем как есть, если это слово, или int если число
            m = int(self.buffer_month) if self.buffer_month.isdigit() else self.buffer_month
            
            self.found_dates.append([d, m, y])
        except ValueError:
            pass # Защита от странных сбоев

    def visualize(self):
        dot = graphviz.Digraph(comment='Date Recognition DFA')
        dot.attr(rankdir='LR')
        
        # Узлы
        dot.node('S', 'START', shape='doublecircle')
        dot.node('D', 'DAY')
        dot.node('Sep1', 'SEP1')
        dot.node('MN', 'MONTH_NUM')
        dot.node('MW', 'MONTH_WORD')
        dot.node('Sep2', 'SEP2')
        dot.node('Y', 'YEAR')
        
        # Ребра
        dot.edge('S', 'D', label='digit')
        dot.edge('D', 'D', label='digit')
        dot.edge('D', 'Sep1', label='dot/space')
        
        dot.edge('Sep1', 'MN', label='digit (if dot)')
        dot.edge('Sep1', 'MW', label='letter (if space)')
        
        dot.edge('MN', 'MN', label='digit')
        dot.edge('MN', 'Sep2', label='dot')
        
        dot.edge('MW', 'MW', label='letter')
        dot.edge('MW', 'Sep2', label='space')
        
        dot.edge('Sep2', 'Y', label='digit')
        dot.edge('Y', 'Y', label='digit')
        dot.edge('Y', 'S', label='other (SAVE)')
        
        return dot

def run_tests():
    dfa = DateDFA()
    
    print("=== ЗАПУСК ТЕСТОВ ===")

    # Тест 1: Пример из задания (смешанный текст)
    text1 = "Событие произошло 2 декабря 1934 года. Ничего не произошло 3.01.2025."
    res1 = dfa.process_text(text1)
    print(f"\nВход: {text1}")
    print(f"Выход: {res1}")
    # Ожидаем: [[2, 'декабря', 1934], [3, 1, 2025]] (или '01' в зависимости от обработки)
    
    # Тест 2: Только даты
    text2 = "12.12.2020 01.05.1999"
    res2 = dfa.process_text(text2)
    print(f"\nВход: {text2}")
    print(f"Выход: {res2}")
    
    # Тест 3: Невалидные даты (шум)
    text3 = "Это 123 декабря, а это 12.привет.2000 и просто число 2025"
    res3 = dfa.process_text(text3)
    print(f"\nВход: {text3}")
    print(f"Выход: {res3}") 
    # Должен игнорировать "123 декабря" (если считаем, что день <= 2 знаков, 
    # но в моем коде выше я разрешил >2 знаков для простоты, 
    # однако "12.привет" сломается на букве после точки).

    try:
        graph = dfa.visualize()
        graph.render('dfa_graph', view=False)
        print("\nГрафическое представление сохранено в файл 'dfa_graph.pdf'")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    run_tests()