from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock


class SortedCategorizer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        # ==================================
        # DATA
        # ==================================
        self.items = []  # [{"id":1,"text":"Ali"}, ...]
        self.selected_id = None
        self.next_id = 1

        self.categories = {
            "LYC": [],
            "ST": [],
            "Pasar": [],
            "AhYam": [],
            "San²": []
            
        }

        self.sorted_categories = {"Pasar" , "San²", "LYC", "ST"}

        # ==================================
        # INPUT
        # ==================================
        self.input = TextInput(
            hint_text="Enter items (one per line)",
            multiline=True,
            size_hint=(1, 0.1)
        )
        self.add_widget(self.input)

        # ==================================
        # ADD BUTTON
        # ==================================
        self.add_btn = Button(
            text="ADD LINES",
            size_hint=(1, 0.05)
        )
        self.add_btn.bind(on_press=self.add_items)
        self.add_widget(self.add_btn)

        # ==================================
        # NEW: TOTAL / UNCATEGORIZED LABEL
        # ==================================
        self.uncategorized_label = Label(
            text="Total: 0 | Uncategorized: 0",
            size_hint=(1, 0.05)
        )
        self.add_widget(self.uncategorized_label)

        # ==================================
        # ITEM LIST
        # ==================================
        self.item_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None
        )
        self.item_box.bind(
            minimum_height=self.item_box.setter("height")
        )

        self.item_scroll = ScrollView(size_hint=(1, 0.25))
        self.item_scroll.add_widget(self.item_box)
        self.add_widget(self.item_scroll)

        # ==================================
        # CATEGORY BUTTONS
        # ==================================
        cat_box = BoxLayout(size_hint=(1, 0.05))

        for cat in self.categories:
            btn = Button(text=cat)
            btn.bind(on_press=self.assign_category)
            cat_box.add_widget(btn)

        self.add_widget(cat_box)

        # ==================================
        # OUTPUT
        # ==================================
        self.output = Label(
            text="No categorized items yet",
            size_hint_y=None,
            valign="top",
            halign="left"
        )

        self.output.bind(texture_size=self.update_output_size)

        output_scroll = ScrollView(size_hint=(1, 0.45))
        output_scroll.add_widget(self.output)
        self.add_widget(output_scroll)

        # ==================================
        # COPY BUTTON
        # ==================================
        self.copy_btn = Button(
            text="COPY RESULT",
            size_hint=(1, 1)
        )
        bottom=BoxLayout(size_hint=(1,0.05))
        self.delete_btn=Button(text="DELETE SELECTED")
        self.delete_btn.bind(on_press=self.delete_selected)
        bottom.add_widget(self.delete_btn)
        self.copy_btn.bind(on_press=self.copy_result)
        bottom.add_widget(self.copy_btn)
        self.add_widget(bottom)

        self.refresh_items()

    # ==================================
    # OUTPUT AUTO SIZE
    # ==================================
    def update_output_size(self, instance, size):
        instance.text_size = (self.width, None)
        instance.height = size[1]

    # ==================================
    # ADD ITEMS
    # ==================================
    def add_items(self, instance):
        for line in self.input.text.splitlines():
            line = line.strip()

            if line:
                self.items.append({
                    "id": self.next_id,
                    "text": line
                })
                self.next_id += 1

        self.input.text = ""
        if self.items:
            self.selected_id=self.items[0]["id"]
        self.refresh_items()
        Clock.schedule_once(lambda dt:self.scroll_to_selected(),0.05)

    # ==================================
    # SELECT ITEM
    # ==================================
    def select_item(self, instance):
        self.selected_id = instance.item_id
        self.refresh_items()

    # ==================================
    # ASSIGN CATEGORY
    # ==================================
    def assign_category(self, instance):
        if self.selected_id is None:
            return

        category = instance.text

        # remove from all categories
        for cat in self.categories:
            if self.selected_id in self.categories[cat]:
                self.categories[cat].remove(self.selected_id)

        current=self.selected_id
        self.categories[category].append(current)
        self.selected_id=None
        for item in self.items:
            if not self.is_categorized(item["id"]):
                self.selected_id=item["id"]
                break
        self.refresh_items()
        Clock.schedule_once(lambda dt:self.scroll_to_selected(),0.05)

    # ==================================
    # GET ITEM TEXT
    # ==================================
    def get_item_text(self, item_id):
        for item in self.items:
            if item["id"] == item_id:
                return item["text"]
        return ""

    # ==================================
    # IS CATEGORIZED
    # ==================================
    def is_categorized(self, item_id):
        for cat in self.categories.values():
            if item_id in cat:
                return True
        return False

    # ==================================
    # NEW: COUNT UNCATEGORIZED ITEMS
    # ==================================
    def get_uncategorized_count(self):
        count = 0

        for item in self.items:
            if not self.is_categorized(item["id"]):
                count += 1

        return count

    # ==================================
    # REFRESH ITEMS
    # ==================================
    def refresh_items(self):
        self.item_box.clear_widgets()

        for item in self.items:

            if item["id"] == self.selected_id:
                color = (0.3, 0.6, 1, 1)
            elif self.is_categorized(item["id"]):
                color = (0.6, 1, 0.6, 1)
            else:
                color = (1, 1, 1, 1)

            btn = Button(
                text=item["text"],
                size_hint_y=None,
                height=70,
                background_color=color
            )

            btn.item_id = item["id"]
            btn.bind(on_press=self.select_item)

            self.item_box.add_widget(btn)

        # NEW: UPDATE TOTAL / UNCATEGORIZED COUNT
        total = len(self.items)
        uncategorized = self.get_uncategorized_count()

        self.uncategorized_label.text = (
            f"Total: {total} | Uncategorized: {uncategorized}"
        )

        self.update_output()


    def scroll_to_selected(self):
        for w in self.item_box.children:
            if getattr(w,"item_id",None)==self.selected_id:
                self.item_scroll.scroll_to(w,padding=20,animate=False)
                break

    # ==================================
    # UPDATE OUTPUT
    # ==================================
    def update_output(self):

        text = ""

        for cat_name, item_ids in self.categories.items():

            count = len(item_ids)

            if count == 1:
                text += f"{cat_name}: (1 item)\n"
            else:
                text += f"{cat_name}: ({count} items)\n"

            names = [
                self.get_item_text(item_id)
                for item_id in item_ids
            ]

            if cat_name in self.sorted_categories:
                names = sorted(names, key=str.lower)

            for name in names:
                text += f"{name}\n"

            text += "\n"

        self.output.text = text.strip()

    # ==================================
    # COPY RESULT
    # ==================================
    def delete_selected(self, instance):
        if self.selected_id is None:
            return
        did=self.selected_id
        self.items=[i for i in self.items if i["id"]!=did]
        for c in self.categories.values():
            if did in c:
                c.remove(did)
        self.selected_id=None
        for item in self.items:
            if not self.is_categorized(item["id"]):
                self.selected_id=item["id"]
                break
        self.refresh_items()
        Clock.schedule_once(lambda dt:self.scroll_to_selected(),0.05)

    def copy_result(self, instance):
        Clipboard.copy(self.output.text)
        self.copy_btn.text = "Copied!"


class MyApp(App):
    def build(self):
        return SortedCategorizer()


if __name__ == "__main__":
    MyApp().run()
  
