from flask import Flask, request, jsonify, render_template

from flask_sqlalchemy import SQLAlchemy  #เพิ่ม import SQLAlchemy


# 1. สร้าง App ของ Flask
app = Flask(__name__)

# 🌐 Route สำหรับเปิดหน้าเว็บหลัก
@app.route("/")
def index():
    return render_template("index.html")


#  เพื่อให้อ่านภาษาไทยตรง ๆ
app.json.ensure_ascii = False


# 👈 2. ตั้งค่าให้เก็บฐานข้อมูลไว้ในไฟล์ชื่อ database.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 👈 3. สร้างตัวจัดการฐานข้อมูล
db = SQLAlchemy(app)


# 4. สร้างโครงสร้างตาราง Todo
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __init__(self, title, completed=False):
        self.title = title
        self.completed = completed



    # ฟังก์ชันแปลงข้อมูลใน Model ให้กลายเป็น Dictionary เพื่อส่งเป็น JSON ได้ง่าย ๆ
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed
        }

# 5. สร้างโครงสร้างตาราง Expense
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), default="ทั่วไป")

    def __init__(self, title, amount, category="ทั่วไป"):
        self.title = title
        self.amount = amount
        self.category = category

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "amount": self.amount,
            "category": self.category
        }





# ********* ระบบ todo list ****************************************

# ********* ระบบ todo list (ใช้ Database) **************************

# 3. Route ดึงรายการ Todo ทั้งหมด (GET)
@app.route("/api/todos", methods=["GET"])
def get_todos():
    # ดึงข้อมูลงานทั้งหมดจากตาราง Todo ใน Database
    todos = Todo.query.all()
    # แปลงข้อมูลแต่ละรายการด้วย .to_dict() แล้วส่งกลับเป็น JSON
    return jsonify([todo.to_dict() for todo in todos])

# 4. Route เพิ่ม Todo ใหม่ (POST)
@app.route("/api/todos", methods=["POST"])
def add_todo():
    data = request.json
    if not data or "title" not in data:
        return jsonify({"error": "กรุณาระบุ title ของงาน"}), 400
    
    # สร้าง Object Todo ใหม่ (ID จะถูกสร้างให้อัตโนมัติ)
    new_todo = Todo(
        title=data["title"],
        completed=False
    )
    
    db.session.add(new_todo)     # เพิ่มเข้าคิว
    db.session.commit()          # บันทึกลงฐานข้อมูลจริง
    
    return jsonify({"message": "เพิ่มงานสำเร็จ!", "todo": new_todo.to_dict()}), 201

# 6. Route แก้ไขงาน (PUT)
@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    # ค้นหางานตาม ID จาก Database
    todo = db.session.get(Todo, todo_id)
    
    if not todo:
        return jsonify({"error": "ไม่พบงานที่ต้องการแก้ไข"}), 404
        
    data = request.json or {}
    if "title" in data:
        todo.title = data["title"]
    if "completed" in data:
        todo.completed = data["completed"]
        
    db.session.commit()  # บันทึกการแก้ไขลงฐานข้อมูล
    return jsonify({"message": "อัปเดตงานสำเร็จ!", "todo": todo.to_dict()})

# 7. Route ลบงาน (DELETE)
@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    
    if not todo:
        return jsonify({"error": "ไม่พบงานที่ต้องการลบ"}), 404
        
    db.session.delete(todo)  # สั่งลบออกจาก Database
    db.session.commit()      # บันทึกผล
    
    return jsonify({"message": f"ลบงาน ID {todo_id} เรียบร้อยแล้ว!"})

#  ***********************  เป็นของ  ระบบ  ค่าใข้จ่ายประจำวัน  ***************

# ********* ระบบ ค่าใช้จ่ายประจำวัน (ใช้ Database) ******************

# 8. Route ดึงรายการค่าใช้จ่ายทั้งหมด + คำนวณยอดเงินรวม (GET)
@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    expenses = Expense.query.all()
    total_amount = sum(item.amount for item in expenses)
    
    return jsonify({
        "expenses": [e.to_dict() for e in expenses],
        "total_amount": total_amount,
        "count": len(expenses)
    })

# 9. Route บันทึกค่าใช้จ่ายใหม่ (POST)
@app.route("/api/expenses", methods=["POST"])
def add_expense():
    data = request.json
    if not data or "title" not in data or "amount" not in data:
        return jsonify({"error": "กรุณาระบุ title และ amount"}), 400
        
    new_expense = Expense(
        title=data["title"],
        amount=float(data["amount"]),
        category=data.get("category", "ทั่วไป")
    )
    
    db.session.add(new_expense)
    db.session.commit()
    
    return jsonify({"message": "บันทึกค่าใช้จ่ายสำเร็จ!", "expense": new_expense.to_dict()}), 201

# 9.1 Route แก้ไขข้อมูลค่าใช้จ่าย (PUT)
@app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    expense = db.session.get(Expense, expense_id)
    
    if not expense:
        return jsonify({"error": "ไม่พบรายการค่าใช้จ่ายที่ต้องการแก้ไข"}), 404
        
    data = request.json or {}
    if "title" in data:
        expense.title = data["title"]
    if "amount" in data:
        expense.amount = float(data["amount"])
    if "category" in data:
        expense.category = data["category"]
        
    db.session.commit()
    return jsonify({"message": "อัปเดตค่าใช้จ่ายสำเร็จ!", "expense": expense.to_dict()})

# 10. Route ลบรายการค่าใช้จ่าย (DELETE)
@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    expense = db.session.get(Expense, expense_id)
    
    if not expense:
        return jsonify({"error": "ไม่พบรายการค่าใช้จ่ายนี้"}), 404
        
    db.session.delete(expense)
    db.session.commit()
    
    return jsonify({"message": f"ลบรายการค่าใช้จ่าย ID {expense_id} แล้ว!"})



# 5. คำสั่งรันเซิร์ฟเวอร์
if __name__ == "__main__":

# สั่งสร้างตารางฐานข้อมูลในไฟล์ database.db ถ้ายังไม่มี
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000, debug=True)


#test