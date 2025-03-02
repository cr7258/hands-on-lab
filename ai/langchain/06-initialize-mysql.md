## 使用 Docker 启动 MySQL

```bash
docker run -d \
  --name mysql-test \
  -e MYSQL_ROOT_PASSWORD=123123 \
  -e MYSQL_DATABASE=test_db8 \
  -p 3306:3306 \
  --restart unless-stopped \
  mysql:8.0
```

## 插入数据

要在 MySQL 中创建一个 **员工表（employee）**，并插入一些数据，可以按照以下步骤进行：

### 连接 MySQL

如果你的 MySQL 运行在 Docker 中，可以用以下命令连接：
```sh
mysql -h 127.0.0.1 -P 3306 -u root -p
```
输入 `123123` 作为密码，进入 MySQL 终端。

###创建数据库（如果尚未创建）
```sql
CREATE DATABASE IF NOT EXISTS test_db;
USE test_db;
```

### 创建员工表
```sql
CREATE TABLE IF NOT EXISTS employee (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    age INT NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL
);
```
- `id`：主键，自增
- `name`：员工姓名
- `age`：年龄
- `department`：部门
- `salary`：薪资（两位小数）


### 插入数据
```sql
INSERT INTO employee (name, age, department, salary) VALUES
('张三', 28, '研发部', 12000.00),
('李四', 32, '市场部', 9000.50),
('王五', 25, '人事部', 8000.00),
('赵六', 30, '财务部', 10000.00),
('程七', 29, '研发部', 52000.00);
```

### 查询数据
```sql
SELECT * FROM employee;
```
