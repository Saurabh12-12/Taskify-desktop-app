"""
🤖 Taskify   (Complete Original Code) python
Smart task manager app with AI insights
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import json
import datetime
import re
from dataclasses import dataclass, asdict
from typing import List, Optional
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import threading
import os

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

@dataclass
class Task:
    id: int
    description: str
    priority_score: float
    urgency_score: float
    sentiment_score: float
    due_date: Optional[datetime.datetime] = None
    completed: bool = False
    created_at: datetime.datetime = None
    category: str = "general"

class Taskify(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("🤖 Taskify")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # AI Components
        self.sia = SentimentIntensityAnalyzer()
        self.tasks: List[Task] = []
        self.next_id = 1
        self.data_file = "Taskify_data.json"
        
        self.load_data()
        self.create_widgets()
        self.update_task_list()
        
    def create_widgets(self):                           #Create all UI components

       
        # Title
        title = ctk.CTkLabel(self, text="🤖 Taskify", 
                           font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=20)
        
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left panel - Add Task & Controls
        left_panel = ctk.CTkFrame(main_frame, width=350)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Add Task Section
        add_frame = ctk.CTkFrame(left_panel)
        add_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(add_frame, text="➕ Add Task", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.task_entry = ctk.CTkEntry(add_frame, height=40, 
                                     placeholder_text="e.g. Finish report by Saturday urgent")
        self.task_entry.pack(fill="x", padx=20, pady=(0, 10))
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        
        add_btn = ctk.CTkButton(add_frame, text="Add Task", height=40,
                              command=self.add_task, fg_color="transparent",
                              border_width=2, corner_radius=10)
        add_btn.pack(fill="x", padx=20, pady=(0, 20))
        
        # Control Buttons

        btn_frame = ctk.CTkFrame(left_panel)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(btn_frame, text="📋 Refresh", width=100,
                     command=self.update_task_list).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="📊 Insights", width=100,
                     command=self.show_insights).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="💾 Save", width=100,
                     command=self.save_data).pack(side="left", padx=5, pady=5)
        
        # Stats

        self.stats_label = ctk.CTkLabel(left_panel, text="📊 Loading...", 
                                      font=ctk.CTkFont(size=14))
        self.stats_label.pack(pady=20)
        
        # Right panel - Task List

        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Task List Header

        header = ctk.CTkLabel(list_frame, text="🎯 AI Prioritized Tasks", 
                            font=ctk.CTkFont(size=18, weight="bold"))
        header.pack(pady=20)
        
        # Treeview for tasks

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Priority", "Task", "Due", "Category"), show="headings", height=20)
        
        # Define columns

        self.tree.heading("ID", text="ID")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Task", text="Task")
        self.tree.heading("Due", text="Due Date")
        self.tree.heading("Category", text="Category")
        
        self.tree.column("ID", width=50)
        self.tree.column("Priority", width=80)
        self.tree.column("Task", width=300)
        self.tree.column("Due", width=120)
        self.tree.column("Category", width=100)
        
        # Scrollbar

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side="right", fill="y", pady=(20, 20))
        
        # Bind double-click to complete task

        self.tree.bind("<Double-1>", self.on_task_double_click)
        
        # Status bar

        self.status_var = tk.StringVar(value="")
        status_bar = ctk.CTkLabel(self, textvariable=self.status_var, 
                                font=ctk.CTkFont(size=12))
        status_bar.pack(side="bottom", fill="x", padx=20, pady=10)
    
    def parse_natural_language(self, text: str) -> dict:
        
        # Urgency detection
        
        urgency_keywords = ['urgent', 'asap', 'now', 'critical']
        urgency_score = sum(1 for word in urgency_keywords if word in text.lower()) * 0.25
        
        # Category detection

        categories = {
            'work': ['work', 'meeting', 'project', 'report'],
            'personal': ['buy', 'shop', 'family'],
            'health': ['gym', 'doctor','medicines']
        }
        category = next((cat for cat, words in categories.items() 
                        if any(w in text.lower() for w in words)), "general")
        
        return {
            'description': text,
            'urgency_score': min(urgency_score, 1.0),
            'category': category
        }
    
    def add_task(self):
        
        text = self.task_entry.get().strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter a task!")
            return
        
        parsed = self.parse_natural_language(text)
        sentiment_score = self.sia.polarity_scores(text)['compound']
        
        task = Task(
            id=self.next_id,
            description=text,
            priority_score=(parsed['urgency_score'] + abs(sentiment_score)) / 2 + 0.3,
            urgency_score=parsed['urgency_score'],
            sentiment_score=sentiment_score,
            created_at=datetime.datetime.now(),
            category=parsed['category']
        )
        
        self.tasks.append(task)
        self.next_id += 1
        self.task_entry.delete(0, 'end')
        self.update_task_list()
        self.save_data()
        self.status_var.set(f"Added task #{task.id}")
    
    def on_task_double_click(self, event):
        
        selection = self.tree.selection()                            #Complete task on double-click
        if selection:
            item = self.tree.item(selection[0])
            task_id = int(item['values'][0])
            
            # Mark as completed
            for task in self.tasks:
                if task.id == task_id:
                    task.completed = True
                    self.update_task_list()
                    self.save_data()
                    self.status_var.set(f"Completed task #{task_id}")
                    break
    
    def update_task_list(self):
        
        # Clear existing items

        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get active tasks sorted by priority

        active_tasks = [t for t in self.tasks if not t.completed]
        active_tasks.sort(key=lambda t: t.priority_score, reverse=True)
        
        for task in active_tasks:
            priority_color = "#ff4444" if task.priority_score > 0.7 else "#ffaa00" if task.priority_score > 0.5 else "#aaa"
            due_str = task.due_date.strftime("%m/%d %H:%M") if task.due_date else ""
            
            self.tree.insert("", "end", values=(
                task.id,
                f"{task.priority_score:.0%}",
                task.description[:50] + "..." if len(task.description) > 50 else task.description,
                due_str,
                task.category.title()
            ))
        
        # Update stats
        insights = self.get_insights()
        self.stats_label.configure(text=f"📊 {insights['pending']}/{insights['total_tasks']} tasks | "
                                      f"{insights['completion_rate']:.0f}% complete")
    
    def get_insights(self) -> dict:
        
        total = len(self.tasks)                                            #Generate productivity insights
        completed = len([t for t in self.tasks if t.completed])
        return {
            'total_tasks': total,
            'pending': total - completed,
            'completed': completed,
            'completion_rate': (completed / total * 100) if total else 0
        }
    
    def show_insights(self):
        
        insights = self.get_insights()                              #Show detailed insights dialog
         
        insight_window = ctk.CTkToplevel(self)
        insight_window.title("📊 AI Insights")
        insight_window.geometry("400x300")
        insight_window.transient(self)
        insight_window.grab_set()
        
        ctk.CTkLabel(insight_window, text="AI Productivity Insights", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        stats_text = f"""
Total Tasks: {insights['total_tasks']}
Pending: {insights['pending']}
Completed: {insights['completed']}
Completion Rate: {insights['completion_rate']:.1f}%

Top Focus: {max(set(t.category for t in self.tasks), key=lambda c: sum(1 for t in self.tasks if t.category == c), default='general').title()}
        """
        
        ctk.CTkLabel(insight_window, text=stats_text, justify="left").pack(pady=20, padx=30)
    
    def save_data(self):
        
        try:
            data = []
            for task in self.tasks:                                  #Save tasks to JSON
                task_data = asdict(task)
                if task_data['created_at']:
                    task_data['created_at'] = task_data['created_at'].isoformat()
                if task_data['due_date']:
                    task_data['due_date'] = task_data['due_date'].isoformat()
                data.append(task_data)
            
            with open(self.data_file, 'w') as f:
                json.dump({'tasks': data, 'next_id': self.next_id}, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")
    
    def load_data(self):
        
        try:
            if os.path.exists(self.data_file):                           #Load tasks from JSON
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = []
                    self.next_id = data.get('next_id', 1)
                    
                    for task_data in data.get('tasks', []):
                        task_data['created_at'] = datetime.datetime.fromisoformat(task_data['created_at'])
                        if task_data.get('due_date'):
                            task_data['due_date'] = datetime.datetime.fromisoformat(task_data['due_date'])
                        self.tasks.append(Task(**task_data))
        except Exception as e:
            print(f"Load error: {e}")

if __name__ == "__main__":
    try:
        # Download NLTK data if needed
        
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        print("📥 Downloading NLTK data...")
        nltk.download('vader_lexicon')
    
    app = Taskify()
    app.mainloop()
