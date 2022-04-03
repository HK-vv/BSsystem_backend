### 接口状态表

| 接口名称                                        | 说明                                     | 完成状态 |
| ----------------------------------------------- | ---------------------------------------- | -------- |
| /api/admin/auth/login                           | 管理员登录                               |          |
| /api/admin/auth/logout                          | 管理员登出                               |          |
| /api/admin/admin_account                        | 创建、删除管理员账号，查看、修改个人信息 |          |
| /api/admin/admin_account/reset_password         | 重置管理员密码                           |          |
| /api/admin/admin_account/list                   | 列出管理员账号                           |          |
| /api/admin/admin_account/integrity_verification | 检测管理员信息是否完整                   |          |
| /api/admin/admin_account/issuper                | 检测是否为超级管理员                     |          |
| /api/admin/user_account/list                    | 列出用户账号                             |          |
| /api/admin/user_account/contest_history         | 列出用户比赛历史                         |          |
| 以上为管理端接口                                |                                          |          |
| /api/user/auth/login                            | 用户登录                                 | 完成     |
| /api/user/auth/logout                           | 用户登出                                 | 完成     |
| /api/user/profile                               | 用户查看、修改个人信息                   | 完成     |
| /api/user/exercise/collect                      | 自主组卷                                 | 完成     |
| /api/user/exercise/problem                      | 获取题面                                 | 完成     |
| /api/user/exercise/problem/check                | 验证答案                                 | 完成     |
| 以上是用户端接口, 以下是通用接口                |                                          |          |
| /api/general/tag/list                           | 获取所有标签                             |          |
|                                                 |                                          |          |