# Copyright 2020 Sophos Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import tkinter
from tkinter.filedialog import askopenfilename, asksaveasfilename

from tkinter import Label
from tkinter import Entry
from tkinter import ttk

import textwrap

from xdr_query_api import ApiError, XDRQueryAPI

TITLE = "XDR Query Interface"
TEXT_FRAME_WIDTH = 115
TEXT_FRAME_HEIGHT = 18
ENCODED_ICON = """R0lGODlhEAAQAPeQAAVguAVguQRiuwRjuwVjuwNmvQRlvARlvQVlvQRmvQRnvghnvQRovwhovRJovBRrvQNrwQRqwANswQNtwwRsw
                  gRuwwNvxANwxQNxxQNxxgJyxwNzxwRwxQV0xwJ2yQN3ygJ4ywN4ywF7zQJ6zAJ6zQF9zwJ8zgJ9zwJ+zw57yBlzwxh2xRh4xhp5xh
                  x5xh54xhx6xxZ9yRh7yBh+yhx+yhx/ygF/0CJzwCR2wA6AzRWBzBaAzBeBzBaBzRyBzByDzRuEzRyEzgGB0QKB0gGD0wKD0wGE1AG
                  F1AGG1QGH1gCI1wGI1wCL2QCM2gGM2gCN2wGO2xeH0DaAxTWDxzeCxjqLzDWR0DWU1Dua1jyb1j+b1j6b10+PylKTy1yZzl+e0k6h
                  2F+t3Gyk03Gl03Gm03Gm1Hmj0Xml0XKq1XGr1nSs1nyu13yw2Yux2I2y2Iu73Z+93oq+4aDA3pHC4ZbH5J7K5Z7L5q7P5rLN5LTN5
                  rLQ5rvT57vW6bzW6cHX6cTb6sTb68/i79Hj8NHk8djm8t7s9OTt9OXt9ubv9vL1+/L3+vT4+/r8/fv8/vz9/v7+/v///wAAAAAAAA
                  AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                  AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                  AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                  AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                  AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAAAAAAAIf8LWE1QIERhdGFYTVA8P3hwYWNrZXQgYmVnaW49J++7vycgaWQ9J1c1TTB
                  NcENlaGlIenJlU3pOVGN6a2M5ZCc/Pgo8eDp4bXBtZXRhIHhtbG5zOng9J2Fkb2JlOm5zOm1ldGEvJyB4OnhtcHRrPSdJbWFnZTo6
                  RXhpZlRvb2wgMTIuMDQnPgo8cmRmOlJERiB4bWxuczpyZGY9J2h0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRhe
                  C1ucyMnPgoKIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PScnCiAgeG1sbnM6dGlmZj0naHR0cDovL25zLmFkb2JlLmNvbS90aW
                  ZmLzEuMC8nPgogIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiA8L3JkZjpEZXNjcmlwdGlvbj4KPC9yZGY
                  6UkRGPgo8L3g6eG1wbWV0YT4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
                  ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
                  CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgIC
                  AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
                  gICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
                  ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
                  CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgIC
                  AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
                  gICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
                  ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
                  CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgIC
                  AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
                  gICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
                  ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
                  CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgIC
                  AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
                  gICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
                  ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
                  CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgIC
                  AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
                  gICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
                  ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
                  CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgIC
                  AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
                  gICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
                  ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
                  CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgIC
                  AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
                  gICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
                  ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
                  CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgIC
                  AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
                  gICAgICAgICAgICAgICAgICAKPD94cGFja2V0IGVuZD0ndyc/PgH//v38+/r5+Pf29fTz8vHw7+7t7Ovq6ejn5uXk4+Lh4N/e3dzb
                  2tnY19bV1NPS0dDPzs3My8rJyMfGxcTDwsHAv769vLu6ubi3trW0s7KxsK+urayrqqmop6alpKOioaCfnp2cm5qZmJeWlZSTkpGQj
                  46NjIuKiYiHhoWEg4KBgH9+fXx7enl4d3Z1dHNycXBvbm1sa2ppaGdmZWRjYmFgX15dXFtaWVhXVlVUU1JRUE9OTUxLSklIR0ZFRE
                  NCQUA/Pj08Ozo5ODc2NTQzMjEwLy4tLCsqKSgnJiUkIyIhIB8eHRwbGhkYFxYVFBMSERAPDg0MCwoJCAcGBQQDAgEAACwAAAAAEAA
                  QAAAI2gCDjLAx5IgSJwidMDkyxMSIHQJNDCmi5CCThQxNmNjxA8SIIUPCzLlj5w6dOBofdhw4x5HLl4McqvQAIoWjQmCyYMEC5opD
                  DzFoZPCww9GgKDZsyBzhIUPQDBs83HnpaFEfKyMyOIVhAWqKN30A/RHkiBCHDBxYwJBQ4ezQDlD1OKoiQcKKFxHqflGThi8bRI7WR
                  ljRRYGCCH6oulzDwDAXPAsMexlDuYyYKREML8DjqA8VAgpAGx5NQMoeqnBwEFjN+oYcxS4TuXkAAIADN4tgU0Vkxowh2AEBADs="""

logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)


class MainWindow(tkinter.Tk):

    def __init__(self):
        super().__init__()

        self.query_api = XDRQueryAPI()

        self.query_text = ""
        self.title(TITLE)

        self.toolbar_icon = tkinter.PhotoImage(data=ENCODED_ICON)
        self.iconphoto(True, self.toolbar_icon)

        self.resizable(False, False)

        component_frame = ttk.Frame(self)
        self.geometry("960x790")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        component_frame.rowconfigure(0, weight=0)
        component_frame.rowconfigure(1, weight=0)

        self.build_menu()

        text_frame = ttk.Frame(component_frame)
        tenant_frame = ttk.Frame(component_frame)
        button_frame = ttk.Frame(component_frame)
        client_frame = ttk.Frame(component_frame)

        component_frame.grid(column=0, row=0, sticky=(tkinter.N, tkinter.S, tkinter.E, tkinter.W))
        text_frame.grid(row=0, column=0, sticky=(tkinter.N, tkinter.W), pady=0, padx=0)
        client_frame.grid(row=1, column=0)
        tenant_frame.grid(row=2, column=0)
        button_frame.grid(row=3, column=0)

        self.build_text_frame(text_frame)
        self.build_client_frame(client_frame)
        self.build_tenant_frame(tenant_frame)
        self.build_button_frame(button_frame)

        self.token = None
        self.whoami = None

    def build_menu(self):
        menubar = tkinter.Menu(self)
        self.config(menu=menubar)
        filemenu = tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load Query", command=self.load_query)
        filemenu.add_command(label="Save Query", command=self.save_query)
        filemenu.add_separator()
        filemenu.add_command(label="Save Output", command=self.save_output)
        filemenu.add_separator()
        filemenu.add_command(label="Load Config", command=self.load_config)
        filemenu.add_command(label="Remove Config", command=self.remove_config)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

    def build_tenant_frame(self, frame):
        label_text = tkinter.StringVar()
        label_text.set("Tenant Id ")
        tenant_label = Label(frame, textvariable=label_text, height=2)
        tenant_label.grid(row=0, column=0)

        self.tenant_entry = Entry(frame, width=50, state='disabled')
        self.tenant_entry.grid(row=0, column=1)

        self.region_label_text = tkinter.StringVar()
        self.region_label = Label(frame, textvariable=self.region_label_text)
        self.region_label_text.set("Environment")
        self.region_label.grid(row=0, column=2)
        self.region_label.grid_forget()

        self.region_combo_box = ttk.Combobox(frame, width=16, state="readonly")
        self.region_combo_box.bind("<FocusIn>", lambda event: event.widget.master.focus_set())
        self.region_combo_box.grid(row=0, column=3)
        self.region_combo_box.grid_forget()

    def build_client_frame(self, frame):
        id_label_text = tkinter.StringVar()
        id_label_text.set("Client Id ")
        client_id_label = Label(frame, textvariable=id_label_text, height=2)
        client_id_label.pack(side="left")

        client_text = tkinter.StringVar()
        client_text.set('Enter api client id')
        self.client_id_entry = Entry(frame, textvariable=client_text, width=50)
        self.client_id_entry.pack(side="left")

        client_secret_text = tkinter.StringVar()
        client_secret_text.set('Enter api client secret')
        self.client_secret_entry = Entry(frame, textvariable=client_secret_text, width=80)
        self.client_secret_entry.pack(side="right")

        secret_label_text = tkinter.StringVar()
        secret_label_text.set("Client Secret ")
        client_secret_label = Label(frame, textvariable=secret_label_text)
        client_secret_label.pack(side="right")

    def build_text_frame(self, frame):
        self.query_frame = ttk.Frame(frame)
        self.query_frame.grid(column=0, row=2, sticky=(tkinter.N, tkinter.W), pady=0, padx=0)

        self.query_scrollbar_v = tkinter.Scrollbar(self.query_frame, orient=tkinter.VERTICAL)
        self.query_scrollbar_v.grid(column=1, row=1, sticky=tkinter.N + tkinter.S)

        self.query_label_text = tkinter.StringVar()
        self.query_label = Label(self.query_frame, textvariable=self.query_label_text)
        self.query_label.grid(column=0, row=0, sticky=(tkinter.N, tkinter.W))
        self.query_label_text.set("Query")

        self.query_text_box = tkinter.Text(self.query_frame, wrap='word', height=TEXT_FRAME_HEIGHT,
                                           width=TEXT_FRAME_WIDTH, yscrollcommand=self.query_scrollbar_v.set)
        self.query_text_box.grid(column=0, row=1, sticky=(tkinter.N, tkinter.W), pady=0, padx=0)
        self.query_text_box.insert(tkinter.END, self.query_text)

        self.query_scrollbar_v.config(command=self.query_text_box.yview)

        self.output_frame = ttk.Frame(frame)
        self.output_frame.grid(column=0, row=3, sticky=(tkinter.N, tkinter.W), pady=0, padx=0)

        self.ouput_label_text = tkinter.StringVar()
        self.output_label = Label(self.output_frame, textvariable=self.ouput_label_text)
        self.output_label.grid(column=0, row=0, sticky=(tkinter.N, tkinter.W))
        self.ouput_label_text.set("Output")

        self.output_scrollbar_v = tkinter.Scrollbar(self.output_frame, orient=tkinter.VERTICAL)
        self.output_scrollbar_v.grid(column=1, row=1, sticky=tkinter.N + tkinter.S)

        self.output_scrollbar_h = tkinter.Scrollbar(self.output_frame, orient=tkinter.HORIZONTAL)
        self.output_scrollbar_h.grid(column=0, row=2, sticky=(tkinter.E + tkinter.W))

        self.output_text_box = tkinter.Text(self.output_frame, wrap='none', height=TEXT_FRAME_HEIGHT,
                                            width=TEXT_FRAME_WIDTH, yscrollcommand=self.output_scrollbar_v.set,
                                            xscrollcommand=self.output_scrollbar_h.set)
        self.output_text_box.grid(column=0, row=1)
        self.output_text_box.configure(state='disabled')

        self.output_scrollbar_v.config(command=self.output_text_box.yview)
        self.output_scrollbar_h.config(command=self.output_text_box.xview)

    def build_button_frame(self, frame):
        self.generate_token_button = tkinter.Button(frame, text="Generate Token", command=self.generate_token)
        self.generate_token_button.grid(column=0, row=1)
        self.query_button = tkinter.Button(frame, text="Run query", command=self.run_query, state='disabled')
        self.query_button.grid(column=1, row=1)

    def load_query(self):
        filename = askopenfilename(parent=self)
        if not filename == '':
            with open(filename) as f:
                self.query_text = f.read()
            self.query_text_box.delete(0.0, tkinter.END)
            self.query_text_box.insert(0.0, self.query_text)

    def save_query(self):
        filename = asksaveasfilename(parent=self)
        if not filename == '':
            with open(filename, 'w') as f:
                f.write(self.query_text_box.get('1.0', tkinter.END))

    def save_output(self):
        filename = asksaveasfilename(parent=self)
        if not filename == '':
            with open(filename, 'w') as f:
                f.write(self.output_text_box.get('1.0', tkinter.END))

    def load_config(self):
        filename = askopenfilename(parent=self)
        try:
            self.query_api.load_config(filename)
            self.load_environment_combo(self.query_api.json_config)
            self.region_label.grid(row=0, column=2)
            self.region_combo_box.grid(row=0, column=3, pady=0, padx=0)
        except ApiError as e:
            self.region_label.grid_forget()
            self.region_combo_box.grid_forget()
            logging.error("Error loading config: " + str(e))
        except FileNotFoundError:
            self.region_label.grid_forget()
            self.region_combo_box.grid_forget()
            logging.error("Config not found")

    def load_environment_combo(self, config):
        combobox_values = []
        for environment in config:
            combobox_values.append(environment)
        self.region_combo_box.config(values=combobox_values)
        self.region_combo_box.current(0)

    def remove_config(self):
        self.region_combo_box.current(0)
        self.region_label.grid_forget()
        self.region_combo_box.grid_forget()
        self.query_api.json_config = ''
        self.tenant_entry.configure(state='normal')
        self.tenant_entry.delete(0, tkinter.END)
        self.tenant_entry.configure(state='disabled')

    def run_query(self):
        query = self.query_text_box.get('1.0', tkinter.END)
        tenant_id = self.tenant_entry.get()

        failed = False
        if not self.token or not self.whoami:
            result = 'Token not set, have you generated a token?'
            failed = True

        if not failed and not tenant_id:
            result = 'Tenant ID not set, have you entered a tenant ID?'
            failed = True

        if not failed:
            try:
                result = self.query_api.run_query(query, tenant_id, self.whoami['apiHosts']['dataRegion'], self.token)
            except ApiError as e:
                result = str(e)

        self.output_text_box.configure(state='normal')
        self.output_text_box.delete(0.0, tkinter.END)
        self.output_text_box.insert(0.0, result)
        self.output_text_box.configure(state='disabled')

    def generate_token(self):
        client_id = self.client_id_entry.get()
        client_secret = self.client_secret_entry.get()
        if self.query_api.json_config != '':
            env = self.region_combo_box.get()
        else:
            env = ''
        try:
            self.token = self.query_api.generate_token(client_id, client_secret, env)
            self.whoami = self.query_api.get_whoami(self.token, env)
            if self.whoami['idType'] == 'tenant':
                self.tenant_entry.configure(state='normal')
                self.tenant_entry.delete(0, tkinter.END)
                self.tenant_entry.insert(0, self.whoami['id'])
                self.tenant_entry.configure(state='disabled')
            else:
                self.tenant_entry.configure(state='normal')
            self.query_button.configure(state='normal')
            wrapper = textwrap.TextWrapper(width=100)
            result = f'Token set to {wrapper.fill(text=self.token)}'
        except ApiError as e:
            result = str(e)

        self.output_text_box.configure(state='normal')
        self.output_text_box.delete(0.0, tkinter.END)
        self.output_text_box.insert(0.0, result)
        self.output_text_box.configure(state='disabled')


def main():
    window = MainWindow()
    window.mainloop()


if __name__ == "__main__":
    main()
