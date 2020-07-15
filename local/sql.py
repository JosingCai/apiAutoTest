from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from flask_sqlalchemy import SQLALchemy

app.secret_key = "yunjikei"
# 配置数据库的修改地址
app.config['SQLALCHEMY_DADABASE_URI'] = "mysql://user:pwd@127.0.0.1/db_name"
# 跟踪数据库的修改 --> 不建议开启 未来的版本中会移除
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLALchemy(app)

# 数据库的模型，需要继承db.Model
class Role(db.Model):
    # 定义表名
    __tablename__ = "roles"

    # 定义字段
    # db.Column表示是一个字段
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)

    # 在一的一方，写关联
    # 表示和User模型发生了关联，增加了一个users属性
    users = db.relationship("User",backref='role')

class User(db.Mode):
    """docstring for Users"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    email = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(32))
    # db.ForeignKey(roles.id) 表示外键，表名.id
    role_id = db.Column(db.Integer, db.ForeignKey(roles.id))
    # User希望有role属性，但是这个属性的定义，需要在另一个模型中定义
    
    def __repr__(self):
        return '<User: %s %s %s %s>' %(self.name, self.id, self.email, self.password)
        
class LoginForm(FlaskForm):
    """docstring for LoginForm"""
    username = StringField('用户名:', validators=[DataRequired()])
    password = PasswordField('密码:', validators=[DataRequired()])
    password2 = PasswordField('确认密码:', validators=[DataRequired(), EqualTo(password), '两次输入的密码不一致'])
    submit = SubmitField('提交')    


if __name__ == '__main__':
    # 删除表
    db.drop_all()
    # 新增表
    db.create_all()

