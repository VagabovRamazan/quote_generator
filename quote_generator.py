import json
import random
import os
from tkinter import *
from tkinter import ttk, messagebox

class RandomQuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("800x750")
        self.root.resizable(True, True)
        
        # Файл для хранения данных
        self.data_file = "quotes.json"
        
        # Загрузка данных
        self.load_data()
        
        # Создание GUI
        self.create_widgets()
        
        # Обновление интерфейса
        self.refresh_history_list()
        self.update_filter_options()
    
    def load_data(self):
        """Загрузка цитат и истории из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.quotes = data.get('quotes', [])
                    self.history = data.get('history', [])
                    self.filtered_history = self.history.copy()  # Для отображения по фильтру
            except:
                self.quotes = []
                self.history = []
                self.filtered_history = []
        else:
            self.quotes = [
                {"text": "Будь изменением, которое ты хочешь видеть в мире.", "author": "Махатма Ганди", "topic": "Мотивация"},
                {"text": "Жизнь — это то, что с тобой происходит, пока ты строишь планы.", "author": "Джон Леннон", "topic": "Жизнь"},
                {"text": "Единственный способ делать великую работу — любить то, что ты делаешь.", "author": "Стив Джобс", "topic": "Работа"},
                {"text": "Не считай дни, делай так, чтобы дни считались.", "author": "Мухаммед Али", "topic": "Мотивация"},
                {"text": "Успех — это способность идти от поражения к поражению, не теряя энтузиазма.", "author": "Уинстон Черчилль", "topic": "Успех"},
                {"text": "Лучшее время посадить дерево было 20 лет назад. Следующее лучшее время — сегодня.", "author": "Китайская пословица", "topic": "Мудрость"},
                {"text": "Воображение важнее знания.", "author": "Альберт Эйнштейн", "topic": "Наука"},
                {"text": "Будьте собой; все остальные роли уже заняты.", "author": "Оскар Уайльд", "topic": "Личность"},
            ]
            self.history = []
            self.filtered_history = []
            self.save_data()
    
    def save_data(self):
        """Сохранение цитат и истории в JSON файл"""
        data = {
            'quotes': self.quotes,
            'history': self.history
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # ОСНОВНОЙ КОНТЕЙНЕР С ПРОКРУТКОЙ
        main_canvas = Canvas(self.root)
        scrollbar = Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = Frame(main_canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Фрейм для вывода цитаты
        self.quote_frame = LabelFrame(self.scrollable_frame, text="📝 Текущая цитата", padx=10, pady=10, font=("Arial", 12, "bold"))
        self.quote_frame.pack(fill=BOTH, padx=10, pady=10, expand=True)
        
        self.quote_text = Text(self.quote_frame, height=4, wrap=WORD, font=("Arial", 12))
        self.quote_text.pack(fill=BOTH, expand=True)
        
        # Кнопка генерации
        self.generate_btn = Button(self.scrollable_frame, text="🎲 Сгенерировать цитату", 
                                   command=self.generate_quote, font=("Arial", 12, "bold"),
                                   bg="#4CAF50", fg="white", pady=5)
        self.generate_btn.pack(pady=10, padx=10, fill=X)
        
        # Фрейм фильтрации
        filter_frame = LabelFrame(self.scrollable_frame, text="🔍 Фильтрация", padx=10, pady=5, font=("Arial", 12, "bold"))
        filter_frame.pack(fill=X, padx=10, pady=5)
        
        Label(filter_frame, text="Автор:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.author_filter = ttk.Combobox(filter_frame, values=["Все"], state="readonly", width=30)
        self.author_filter.grid(row=0, column=1, padx=5, pady=5)
        self.author_filter.set("Все")
        self.author_filter.bind('<<ComboboxSelected>>', self.auto_apply_filter)  # Автоприменение
        
        Label(filter_frame, text="Тема:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky=W)
        self.topic_filter = ttk.Combobox(filter_frame, values=["Все"], state="readonly", width=25)
        self.topic_filter.grid(row=0, column=3, padx=5, pady=5)
        self.topic_filter.set("Все")
        self.topic_filter.bind('<<ComboboxSelected>>', self.auto_apply_filter)  # Автоприменение
        
        # Кнопки фильтрации
        btn_frame = Frame(filter_frame)
        btn_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        self.reset_filter_btn = Button(btn_frame, text="🔄 Сбросить фильтры", 
                                       command=self.reset_filters, bg="#FF9800", fg="white",
                                       font=("Arial", 10), padx=10)
        self.reset_filter_btn.pack(side=LEFT, padx=5)
        
        # Информация о текущем фильтре
        self.filter_info_label = Label(self.scrollable_frame, text="🏷️ Фильтр не активен", 
                                       fg="blue", font=("Arial", 9, "italic"))
        self.filter_info_label.pack(pady=5)
        
        # Фрейм истории
        history_frame = LabelFrame(self.scrollable_frame, text="📜 История цитат (отфильтрованная)", 
                                   padx=10, pady=5, font=("Arial", 12, "bold"))
        history_frame.pack(fill=BOTH, padx=10, pady=10, expand=True)
        
        history_scrollbar = Scrollbar(history_frame)
        history_scrollbar.pack(side=RIGHT, fill=Y)
        
        self.history_listbox = Listbox(history_frame, yscrollcommand=history_scrollbar.set, 
                                       height=8, font=("Arial", 10))
        self.history_listbox.pack(fill=BOTH, expand=True)
        history_scrollbar.config(command=self.history_listbox.yview)
        
        # Фрейм добавления новой цитаты
        add_frame = LabelFrame(self.scrollable_frame, text="➕ Добавить новую цитату", padx=10, pady=10, font=("Arial", 12, "bold"))
        add_frame.pack(fill=X, padx=10, pady=10)
        
        Label(add_frame, text="📖 Текст цитаты:", font=("Arial", 10, "bold")).pack(anchor=W, pady=(5,0))
        self.new_text = Text(add_frame, height=3, wrap=WORD, font=("Arial", 10))
        self.new_text.pack(fill=X, pady=5)
        
        Label(add_frame, text="✍️ Автор:", font=("Arial", 10, "bold")).pack(anchor=W, pady=(5,0))
        self.new_author = Entry(add_frame, width=40, font=("Arial", 10))
        self.new_author.pack(fill=X, pady=5)
        
        Label(add_frame, text="🏷️ Тема:", font=("Arial", 10, "bold")).pack(anchor=W, pady=(5,0))
        self.new_topic = Entry(add_frame, width=30, font=("Arial", 10))
        self.new_topic.pack(fill=X, pady=5)
        
        self.add_btn = Button(add_frame, text="💾 СОХРАНИТЬ ЦИТАТУ", 
                              command=self.add_quote,
                              bg="#4CAF50", fg="white", 
                              font=("Arial", 12, "bold"),
                              padx=20, pady=10)
        self.add_btn.pack(pady=15)
        
        Label(self.scrollable_frame, text="").pack()
    
    def auto_apply_filter(self, event=None):
        """Автоматическое применение фильтра при выборе"""
        self.apply_filter(show_message=False)
    
    def apply_filter(self, show_message=True):
        """Применение фильтров и обновление отображения истории"""
        author = self.author_filter.get()
        topic = self.topic_filter.get()
        
        # Фильтруем историю
        self.filtered_history = self.history.copy()
        
        if author != "Все":
            self.filtered_history = [q for q in self.filtered_history if q["author"] == author]
        
        if topic != "Все":
            self.filtered_history = [q for q in self.filtered_history if q["topic"] == topic]
        
        # Обновляем отображение
        self.refresh_history_list()
        
        # Обновляем информацию о фильтре
        if author == "Все" and topic == "Все":
            self.filter_info_label.config(text="🏷️ Фильтр не активен (показываются все цитаты)", fg="blue")
            if show_message:
                messagebox.showinfo("Фильтр", "Фильтр сброшен. Показываются все цитаты из истории.")
        else:
            filter_text = []
            if author != "Все":
                filter_text.append(f"автор: {author}")
            if topic != "Все":
                filter_text.append(f"тема: {topic}")
            filter_str = ", ".join(filter_text)
            self.filter_info_label.config(text=f"🔍 Активен фильтр: {filter_str} (найдено в истории: {len(self.filtered_history)})", fg="green")
            
            if show_message:
                # Находим цитаты в общей базе по фильтру
                filtered_quotes = self.get_filtered_quotes()
                messagebox.showinfo("Фильтр применён", 
                                   f"Выбран фильтр: {filter_str}\n"
                                   f"Найдено цитат в базе: {len(filtered_quotes)}\n"
                                   f"Найдено в истории: {len(self.filtered_history)}\n\n"
                                   f"В истории отображаются только цитаты, соответствующие фильтру.")
    
    def generate_quote(self):
        """Генерация случайной цитаты с учётом фильтров"""
        # Получаем отфильтрованные цитаты
        filtered_quotes = self.get_filtered_quotes()
        
        if not filtered_quotes:
            messagebox.showwarning("Нет цитат", 
                                  "Нет цитат, соответствующих выбранным фильтрам!\n"
                                  "Пожалуйста, измените фильтры или добавьте новую цитату.")
            return
        
        # Выбираем случайную цитату
        quote = random.choice(filtered_quotes)
        
        # Отображаем в текстовом поле
        display_text = f'"{quote["text"]}"\n\n— {quote["author"]} ({quote["topic"]})'
        self.quote_text.delete(1.0, END)
        self.quote_text.insert(1.0, display_text)
        
        # Добавляем в историю
        self.history.append(quote)
        
        # Применяем текущий фильтр к новой истории
        self.apply_filter(show_message=False)
        
        # Сохраняем данные
        self.save_data()
    
    def get_filtered_quotes(self):
        """Получение цитат из БАЗЫ с учётом фильтров"""
        author = self.author_filter.get()
        topic = self.topic_filter.get()
        
        filtered = self.quotes.copy()
        
        if author != "Все":
            filtered = [q for q in filtered if q["author"] == author]
        
        if topic != "Все":
            filtered = [q for q in filtered if q["topic"] == topic]
        
        return filtered
    
    def reset_filters(self):
        """Сброс всех фильтров и показ всей истории"""
        self.author_filter.set("Все")
        self.topic_filter.set("Все")
        self.apply_filter(show_message=True)
        self.update_filter_options()
    
    def update_filter_options(self):
        """Обновление доступных опций в выпадающих списках"""
        authors = sorted(set([q["author"] for q in self.quotes]))
        topics = sorted(set([q["topic"] for q in self.quotes]))
        
        self.author_filter['values'] = ["Все"] + authors
        self.topic_filter['values'] = ["Все"] + topics
    
    def refresh_history_list(self):
        """Обновление списка истории (показывает отфильтрованную историю)"""
        self.history_listbox.delete(0, END)
        
        if not self.filtered_history:
            author = self.author_filter.get()
            topic = self.topic_filter.get()
            
            if author != "Все" or topic != "Все":
                filter_text = []
                if author != "Все":
                    filter_text.append(f"автору '{author}'")
                if topic != "Все":
                    filter_text.append(f"теме '{topic}'")
                self.history_listbox.insert(END, f"📭 Нет цитат в истории, соответствующих фильтру по {', '.join(filter_text)}")
                self.history_listbox.insert(END, "💡 Совет: сгенерируйте новую цитату с этим фильтром!")
            else:
                self.history_listbox.insert(END, "📭 История пуста. Нажмите 'Сгенерировать цитату'!")
            return
        
        # Показываем отфильтрованную историю
        for i, quote in enumerate(self.filtered_history[-20:], 1):
            quote_text = quote["text"][:47] + "..." if len(quote["text"]) > 50 else quote["text"]
            display = f"{i}. {quote_text} — {quote['author']} ({quote['topic']})"
            self.history_listbox.insert(END, display)
        
        # Добавляем информацию о количестве
        total_in_history = len(self.history)
        if len(self.filtered_history) < total_in_history:
            self.history_listbox.insert(END, "")
            self.history_listbox.insert(END, f"--- Показано {len(self.filtered_history)} из {total_in_history} цитат в истории ---")
    
    def add_quote(self):
        """Добавление новой цитаты с проверкой ввода"""
        text = self.new_text.get(1.0, END).strip()
        author = self.new_author.get().strip()
        topic = self.new_topic.get().strip()
        
        if not text:
            messagebox.showerror("Ошибка", "❌ Текст цитаты не может быть пустым!")
            return
        if not author:
            messagebox.showerror("Ошибка", "❌ Автор не может быть пустым!")
            return
        if not topic:
            messagebox.showerror("Ошибка", "❌ Тема не может быть пустой!")
            return
        
        new_quote = {"text": text, "author": author, "topic": topic}
        self.quotes.append(new_quote)
        
        self.new_text.delete(1.0, END)
        self.new_author.delete(0, END)
        self.new_topic.delete(0, END)
        
        self.save_data()
        self.update_filter_options()
        
        messagebox.showinfo("Успех", f"✅ Цитата успешно добавлена!\n\n📖 {text[:50]}...\n✍️ {author}\n🏷️ {topic}")
        
        if messagebox.askyesno("Генерация", "Хотите сразу сгенерировать эту цитату?"):
            display_text = f'"{text}"\n\n— {author} ({topic})'
            self.quote_text.delete(1.0, END)
            self.quote_text.insert(1.0, display_text)
            
            self.history.append(new_quote)
            self.apply_filter(show_message=False)
            self.save_data()

if __name__ == "__main__":
    root = Tk()
    app = RandomQuoteGenerator(root)
    root.mainloop()