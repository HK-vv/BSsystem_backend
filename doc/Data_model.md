# 数据库表定义

### BSUser

| 列名     | 数据类型及精度 | 约束条件         | 说明               | 备注      |
| :------- | -------------- | ---------------- | ------------------ | --------- |
| openid   | varchar(30)    | PRIMARY KEY      | 微信提供的唯一标识 |           |
| username | varchar(20)    | UNIQUE, NOT NULL | 用户名             |           |
| rating   | int            | NOT NULL         | 分数               | 初始化为0 |

### BSAdmin

| 列名     | 数据类型及精度 | 约束条件                    | 说明     | 备注     |
| -------- | -------------- | --------------------------- | -------- | -------- |
| id       | int            | PRIMARY KEY, AUTO_INCREMENT | 唯一标识 |          |
| username | varchar(20)    | UNIQUE, NOT NULL            | 用户名   |          |
| password | varchar(20)    | NOT NULL                    | 密码     |          |
| email    | varchar(30)    |                             | 电子邮箱 | 前端检查 |
| phone    | varchar(20)    |                             | 电话     | 前端检查 |

### Problem

| 列名        | 数据类型及精度 | 约束条件                                                  | 说明       | 备注                                                         |
| ----------- | -------------- | --------------------------------------------------------- | ---------- | ------------------------------------------------------------ |
| id          | int            | PRIMARY KEY, AUTO_INCREMENT                               | 唯一标识   |                                                              |
| description | varchar(200)   | NOT NULL                                                  | 题目描述   |                                                              |
| type        | varchar(20)    | NOT NULL, CHECK(type in {"单选", "多选", "判断", "填空"}) | 题目类型   |                                                              |
| A           | varchar(50)    |                                                           | A选项      | 题目类型为填空时为空                                         |
| B           | varchar(50)    |                                                           | B选项      | 题目类型为填空时为空                                         |
| C           | varchar(50)    |                                                           | C选项      | 题目类型为判断、填空时为空                                   |
| D           | varchar(50)    |                                                           | D选项      | 题目类型为判断、填空时为空                                   |
| answer      | varchar(100)   | NOT NULL                                                  | 答案       | 如果有多个空，用逗号(,)隔开；如果答案有多种，用左斜杠(/)隔开 |
| public      | boolean        | NOT NULL                                                  | 题目公开性 |                                                              |
| authorid    | int            | FOREIGN KEY(Admin(id))                                    | 作者id     |                                                              |

### Tag

| 列名 | 数据类型及精度 | 约束条件                    | 说明     | 备注         |
| ---- | -------------- | --------------------------- | -------- | ------------ |
| id   | int            | PRIMARY KEY, AUTO_INCREMENT | 唯一标识 |              |
| name | varchar(20)    | UNIQUE, NOT NULL            | 标签名称 | 不能含有符号 |

### ProblemTag

| 列名      | 数据类型及精度 | 约束条件                 | 说明   | 备注 |
| --------- | -------------- | ------------------------ | ------ | ---- |
| problemid | int            | FOREIGN KEY(Problem(id)) | 题目id |      |
| tagid     | int            | FOREIGN KEY(Tag(id))     | 标签id |      |

### Contest

| 列名     | 数据类型及精度 | 约束条件                    | 说明         | 备注               |
| -------- | -------------- | --------------------------- | ------------ | ------------------ |
| id       | int            | PRIMARY KEY, AUTO_INCREMENT | 唯一标识     |                    |
| name     | varchar(30)    | NOT NULL, UNIQUE            | 竞赛名称     |                    |
| start    | datetime       | NOT NULL                    | 竞赛开始时间 |                    |
| latest   | datetime       | NOT NULL                    | 最晚进入时间 |                    |
| password | varchar(30)    |                             | 比赛密码     | 为NULL代表比赛公开 |
| rated    | boolean        | NOT NULL                    | 是否计分     |                    |
| authorid | int            | FOREIGN KEY(Admin(id))      | 作者id       |                    |

### ContestProblem

| 列名                   | 数据类型及精度 | 约束条件                 | 说明        | 备注 |
| ---------------------- | -------------- | ------------------------ | ----------- | ---- |
| contestid              | int            | FOREIGN KEY(Contest(id)) | 比赛id      |      |
| problemid              | int            | FOREIGN KEY(Problem(id)) | 题目id      |      |
| (problemid, contestid) |                | INDEX                    | 索引        |      |
| number                 | int            | NOT NULL, UNIQUE         | 题目序号    |      |
| duration               | int            | NOT NULL                 | 题目时限(s) |      |

### Registration

| 列名                | 数据类型及精度 | 约束条件                    | 说明               | 备注                                             |
| ------------------- | -------------- | --------------------------- | ------------------ | ------------------------------------------------ |
| id                  | int            | PRIMARY KEY, AUTO_INCREMENT | 注册id             |                                                  |
| userid              | varchar(30)    | FOREIGN KEY(User(id))       | 用户id             |                                                  |
| contestid           | int            | FOREIGN KEY(Contest(id))    | 比赛id             |                                                  |
| (userid, contestid) |                | INDEX                       | 索引               |                                                  |
| regtime             | datetime       | NOT NULL                    | 登记比赛时间       |                                                  |
| starttime           | datetime       |                             | 开始比赛时间       |                                                  |
| currentnumber       | int            | NOT NULL                    | 当前做到的题号     | 注册时初始化为0                                  |
| currenttime         | datetime       |                             | 当前题目的开始时间 | 实际上为上一道题提交时间(第一题则是开始比赛时间) |
| correct             | int            |                             | 正确数量           |                                                  |
| timecost            | int            |                             | 总耗时(s)          | 比赛结束后即是$currenttime-starttime$            |
| score               | int            |                             | 得分               |                                                  |
| rank                | int            |                             | 排名               |                                                  |
| beforerating        | int            |                             | 更新前rating       |                                                  |
| afterrating         | int            |                             | 更新后rating       |                                                  |

### Record

| 列名                    | 数据类型及精度 | 约束条件                                              | 说明         | 备注 |
| ----------------------- | -------------- | ----------------------------------------------------- | ------------ | ---- |
| registerid              | int            | FOREIGN KEY(Registration)                             | 注册id       |      |
| problemno               | int            |                                                       | 题目序号     |      |
| (registerid, problemno) |                | INDEX                                                 | 索引         |      |
| result                  | varchar(10)    | NOT NULL, CHECK(result in {"正确", "错误", "未作答"}) | 题目作答结果 |      |
| submitted               | varchar(100)   |                                                       | 提交的答案   |      |