API Server 作为 Kubernetes 的网关，是用户访问和管理资源对象的入口。对于每个访问请求， API Server 都需要对访问者的合法性进行检查，包括身份验证、权限验证等等。Kubernetes 支持多种身份验证的方式，本文将对 OpenID Connect 认证进行介绍。

## 1 OpenID Connect（OIDC）介绍

OAuth（Open Authorization）是一个关于授权（authorization）的开放网络标准，允许用户授权第三方应用访问他们存储在其他服务提供者上的信息，而不需要将用户名和密码提供给第三方应用。OAuth 在全世界得到了广泛的应用，目前的版本是 2.0 。

OpenID Connect (OIDC) 是一种身份验证协议，基于 OAuth 2.0 系列规范。OAuth2 提供了 `access_token` 来解决授权第三方客户端访问受保护资源的问题，OpenID Connect 在这个基础上提供了 `id_token` 来解决第三方客户端**标识用户身份**的问题。

OpenID Connect 的核心在于，在 OAuth2 的授权流程中，同时提供用户的身份信息（`id_token`）给到第三方客户端。`id_token` 使用JWT（JSON Web Token）格式进行封装，得益于 JWT 的自包含性，紧凑性以及防篡改机制等特点，使得 `id_token` 可以安全地传递给第三方客户端程序并且易于验证。

JSON Web Token（JWT）是一个开放的行业标准（RFC 7519），它定义了一种简洁的、自包含
的协议格式，用于在通信双方间传递 JSON 对象，传递的信息经过数字签名可以被验证和信任。想要了解 JWT 的详细内容参见 [JWT（JSON Web Token）](https://mp.weixin.qq.com/s/I7bLJ-Kux1nhsHYzQnQWNQ)。

## 2 Kubernetes OpenID Connect  认证流程
在 Kubernetes 中 OpenID Connect 的认证流程如下：
- 1.用户登录认证服务器。
- 2.认证服务器返回 `access_token`、`id_token` 和 `refresh_token`。
- 3.在使用 kubectl 时，将 `id_token` 设置为 `--token` 的参数值，或者将其直接添加到 kubeconfig 中。
- 4.kubectl 将 `id_token` 添加到 HTTP 请求的 `Authorization` 头部中，发送给 API  Server。
- 5.API Server 通过检查配置中引用的证书来确认 JWT 的签名是否合法。
- 6.API Server 检查 id_token 是否过期。
- 7.API Server 确认用户是否有操作资源的权限。
- 8.鉴权成功之后，API 服务器向 kubectl 返回响应。
- 9.kubectl 向用户返回结果。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405130513.png)

## 3 Keycloak 介绍
本文将会使用 Keycloak 作为 OpenID Connect 的认证服务器。[keycloak](https://www.keycloak.org/) 是一个开源的、面向现代应用和服务的 IAM（身份认证和访问控制）解决方案。Keycloak 提供了单点登录（SSO）功能，支持 `OpenID Connect`、`OAuth 2.0`、`SAML 2.0` 等协议，同时 Keycloak 也支持集成不同的身份认证服务，例如 LDAP、Active Directory、Github、Google 和 Facebook 等等。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405125805.png)

在 Keycloak 中有以下几个主要概念：
- **领域（realms）**：领域管理着一批用户、证书、角色、组等等，不同领域之间的资源是相互隔离的，实现了多租户的效果。
- **客户端（clients）**：需要接入 Keycloak 实现用户认证的应用和服务。
- **用户（users）**：用户是能够登录到应用系统的实体，拥有相关的属性，例如电子邮件、用户名、地址、电话号码和生日等等。
- **组（groups）**：一组用户的集合，你可以将一系列的角色赋予定义好的用户组，一旦某用户属于该用户组，那么该用户将获得对应组的所有角色权限。
- **角色（roles）**：角色是 RBAC 的重要概念，用于表明用户的身份类型。
- **证书（credential）**：Keycloak 用于验证用户的凭证，例如密码、一次性密码、证书、指纹等等。

## 4 前提条件
接下来的章节将演示如何部署和配置 Keycloak 服务作为 API Server 的认证服务，需要确保完成了以下准备：
- 部署好一套 Kubernetes 集群，我使用的集群版本是 v1.23.5。
- 一台安装好 Docker 和 Docker Compose 的机器，用于部署 Keycloak 服务器。

本实验使用的配置文件可以在：https://github.com/cr7258/kubernetes-guide/authentication/openid 中获取。

## 5 部署 Keycloak 服务器
Kubernetes 要求使用的  OpenID Connect 认证服务必须是 HTTPS 加密的，运行以下脚本生成 Keycloak 服务器的私钥和证书签名请求，并使用 Kubernetes 的 CA 证书进行签发，当然这里你也可以另外生成自己的 CA 证书进行签发，如果这样做的话，请注意在 **7.1 启用 OpenID Connect  认证**章节中将 CA 证书挂载进 API Server 容器中。
```bash
#!/bin/bash
# 创建目录存放生成的证书
mkdir -p ssl

# 生成 x509 v3 扩展文件
cat << EOF > ssl/req.cnf
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
[req_distinguished_name]
[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = IP:11.8.36.25  # Keycloak 服务器的 IP 地址
EOF

# 生成 Keycloak 服务器私钥
openssl genrsa -out ssl/tls.key 2048
# 生成 Keycloak 服务器证书签名请求（CSR）
openssl req -new -key ssl/tls.key -out ssl/tls.csr -subj "/CN=Keycloak" -config ssl/req.cnf
# 使用 CA 签发 Keycloak 服务器证书
openssl x509 -req -in ssl/tls.csr -CA /etc/kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial -out ssl/tls.crt -days 10 -extensions v3_req -extfile ssl/req.cnf
```

这里使用 `docker-compose` 部署 Keycloak 以及依赖的数据库 PostgreSQL，docker-compose.yml 文件如下。需要将上面生成的服务器证书 tls.crt 和服务器私钥 tls.key 两个文件挂载到 Keycloak 容器的 /etc/x509/https 目录中。
```bash
version: '2'
services:
  postgres:
      image: postgres:12.2
      environment:
        POSTGRES_DB: keycloak
        POSTGRES_USER: keycloak
        POSTGRES_PASSWORD: keycloak
  keycloak:
      image: jboss/keycloak:16.1.1
      environment:
        DB_VENDOR: POSTGRES
        DB_ADDR: postgres
        DB_DATABASE: keycloak
        DB_USER: keycloak
        DB_PASSWORD: keycloak
        KEYCLOAK_USER: admin # 用户名 
        KEYCLOAK_PASSWORD: czw123456 # 密码
      volumes:
        - ./ssl:/etc/x509/https # 将服务器证书和私钥挂载到容器中
      ports:
        - 80:8080
        - 443:8443
      depends_on:
        - postgres
```
在后台启动 Keycloak 容器。
```bash
docker-compose up -d 
```
确认 Keycloak 和 PostgreSQL 已经成功启动。
```bash
docker-compose ps
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405132635.png)

浏览器输入 https://<IP 地址>:8443，访问 Keycloak 界面，用户名：admin，密码：czw123456。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220402131436.png)

## 6 配置 Keycloak
### 6.1 创建 Realm
首先，创建一个名称为  **project-1** 的 `Realm`（领域）。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405133133.png)
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405134352.png)

### 6.2 创建 User
接下来手动创建一个用户。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405140758.png)

用户名设置为 tom。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405140731.png)

设置用户的密码，将 Temporary 参数置为 OFF，表示用户在第一次登陆时无需重新设置密码。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405140828.png)

为用户添加属性 name，值设置为 tom，在 **6.3 创建 Client** 章节中会说明为什么这么做。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405141108.png)

查看创建的用户。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405171238.png)
### 6.3 创建 Client
`Client` （客户端）是请求 Keycloak 对用户进行身份验证的客户端，在本示例场景中，API Server 相当于一个客户端，负责向 Keycloak 发起身份认证请求。创建一个名为 **kubernetes** 的客户端，使用 openid-connect 协议对接。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405134229.png)
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405134330.png)

客户端创建完成后，需要修改客户端的  `Access Type` 为 **confidential**，表示客户端通过 `client secret` 来获取令牌；`Valid Redirect URIs` 用于设置浏览器登录成功后有效的重定向 URL，**http://*** 匹配所有 HTTP 重定向的网址。默认情况下，登录成功后将会重定向到 http://localhost:8000。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405221343.png)


要想让 Kubernetes 认识 Keycloak 中的用户，就需要在 Keycloak 返回的 id_token 中携带表明用户的身份的信息（例如用户名、组、邮箱等等），Keycloak 支持自定义声明并将它们添加到 id_token 中。如下所示，在 kubernetes 客户端中创建一个名为 name 的映射。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405141216.png)

Keycloak 会将 `Token Claim Name` 中设置的内容作为键注入 JWT，值的内容来自 **6.2 创建 User** 章节中在用户属性中设置的 name 字段的值。也就是说在 JTW 的 payload 中可以看到 `name:tom` 这个键值对，在 **7.1 启用 OpenID Connect  认证**章节中将会使用 `--oidc-username-claim=name`  参数指定读取 JWT 中 name 字段的值作为用户名。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405141315.png)

查看创建的 mapper。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405142118.png)

### 6.4 延长 Token 时间（可选）
Keycloak 中设置的 access_token 和 id_token 的有效期默认是 1 分钟，为了方便后续的实验，这里将令牌的有效期延长至 30 分钟。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405142818.png)

### 6.5 查看端点信息
点击 Realm Settings -> General -> Endpoints 可以看到请求 project-1 这个 `Realm` 相关的端点信息，在后面的章节中将会用到这些信息。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405172246.png)

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405172316.png)

## 7 配置 Kubernetes
### 7.1 启用 OpenID Connect  认证
要启用 OpenID Connect 认证，需要在 API Server 容器的启动参数中添加以下配置：
- **--oidc-issuer-url**：OpenID Connect 认证服务器的地址，只接受 HTTPS 加密的地址。
- **--oidc-client-id**：客户端 ID。
- **--oidc-username**：从 JWT Claim 中获取用户名的字段。
- **--oidc-username-claim**：添加到 JWT Claim 中的用户名前缀，用于避免与现有的用户名产生冲突。例如，此标志值为 `oidc:` 时将创建形如 `oidc:tom` 的用户名，**此标志值为 `-` 时，意味着禁止添加用户名前缀。** 如果你为用户名添加的前缀是以 `:` 结尾的，在设置 API Server 时请用双引号包围，例如 `"--oidc-username-prefix=oidc:"` 。
- **--oidc-ca-file**：签发 Keycloak 服务器证书的 CA 证书路径，如果签发证书的是受信任的 CA 机构，不用设置该参数。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405173048.png)

关于 OpenID Connect 设置的参数详情参见 [openid-connect-tokens](https://kubernetes.io/docs/reference/access-authn-authz/authentication/#openid-connect-tokens)。
### 7.2 设置 RBAC
创建一个名为 namespace-view 的角色，该角色拥有 namespaces 资源的读取权限，然后将该角色和用户 tom 进行绑定。
```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: namespace-view
rules:
  - apiGroups: [""]
    resources: ["namespaces"] 
    verbs: ["get", "watch", "list"] # 允许读取 namespace 信息
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: tom-crb
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: namespace-view # 关联的角色
subjects:
- kind: User
  name: tom  # 用户名
  apiGroup: rbac.authorization.k8s.io
```

## 8 获取身份验证令牌
现在我们已经完成了 Keycloak 和 Kubernetes 的设置，接下来我们尝试获取身份验证令牌，需要提供以下参数：
- **grant_type**：获取令牌的方式。OAuth 2.0 规定了四种获取令牌的方式，分别是：授权码（authorization-code）、隐藏式（implicit）、密码式（password）、客户端凭证（client credentials）。password 表示以密码的方式获取令牌。
-  **client_id**：客户端 ID。
-  **client_secret**：客户端密钥。
-  **username**：用户名。
-  **password**：密码。
- **scope**：要求的授权范围，OpenID Connect 的请求 scope 设置为 openid。

client_secret 可以在 kubernetes 客户端的 Credentials 中获取；请求的 URL 使用 **6.5 查看端点信息**章节中看到的 **token_endpoint** 的地址。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405140932.png)

```bash
curl -ks -X POST https://11.8.36.25/auth/realms/project-1/protocol/openid-connect/token \
-d grant_type=password -d client_id=kubernetes \
-d username=tom -d password=tom123456 -d scope=openid \
-d client_secret=YsXXff8TL5EXNmSpTeDLdKf99cYBLqqq
```
以上命令将会返回 3 个令牌：access_token，id_token，refresh_token，令牌的有效期为 30 分钟（1800 秒）。
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJZUFB3M0l2MHQ5WHEzMW0zLUtCemgyaHk3Um1LSEJ5dEtIdWhHSWY4Vkw0In0.eyJleHAiOjE2NDkxNTQ3MzgsImlhdCI6MTY0OTE1MjkzOCwianRpIjoiOTZmYzY2ZWMtMTFjNC00Y2JkLTkwNWYtMDhjMGQ4ODkyNjc3IiwiaXNzIjoiaHR0cHM6Ly8xMS44LjM2LjI1L2F1dGgvcmVhbG1zL3Byb2plY3QtMSIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiIwNGVjMDdjMy1mZjY0LTRjZDUtYTc3ZS03MzllOWU3OWVjMmIiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJrdWJlcm5ldGVzIiwic2Vzc2lvbl9zdGF0ZSI6IjQ1ODY1NjM2LTIyMTgtNGE0MC1hZDJlLTkzZGUyYmVkYmQzYiIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJkZWZhdWx0LXJvbGVzLXByb2plY3QtMSIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInNpZCI6IjQ1ODY1NjM2LTIyMTgtNGE0MC1hZDJlLTkzZGUyYmVkYmQzYiIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6InRvbSIsInByZWZlcnJlZF91c2VybmFtZSI6InRvbSJ9.h9F09-OZ9mFR4D6eUQ4lrTSRiSTcTXa8Kzd6B5NuWj7i_WpN4Lx_LKk9lVzb5Mh7ZeQScueYrTQ1ckn59MZdvZ3Y1c-zM8qhYsekSXLNk4HF9ijlIPi7NtlMdA_YUUc5IwcdzfSFJtcyP51CIsOxDto9-mwttlN1Cc-SotviTk4WEpy_T-Y4ZXFlBhrLjrx3o17nvMtEeM3SZbs2OlmlwnKNGs7AMC5FFq5hD-F_9eBR5GclIcLITsxLgRBI9QaSoWVWIVuvUSap04whHLLlQKKqo9sCr5bSUNRBDCCGhu3JLI5-wFZL8k59XSlxOu5MT7DeA8bXmkRdepUxfF6QWA",
  "expires_in": 1800, # access_token 和 id_token 的过期时间
  "refresh_expires_in": 1800, # refresh_token 的过期时间
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI3ZjMyMzBkNS0xNzZhLTQ1YjktOTUxNC0xZjBhY2JmODdhMzMifQ.eyJleHAiOjE2NDkxNTQ3MzgsImlhdCI6MTY0OTE1MjkzOCwianRpIjoiZTRjODllN2ItODllZi00MDFjLWEwZGMtZmQxZjc2MGMxN2UyIiwiaXNzIjoiaHR0cHM6Ly8xMS44LjM2LjI1L2F1dGgvcmVhbG1zL3Byb2plY3QtMSIsImF1ZCI6Imh0dHBzOi8vMTEuOC4zNi4yNS9hdXRoL3JlYWxtcy9wcm9qZWN0LTEiLCJzdWIiOiIwNGVjMDdjMy1mZjY0LTRjZDUtYTc3ZS03MzllOWU3OWVjMmIiLCJ0eXAiOiJSZWZyZXNoIiwiYXpwIjoia3ViZXJuZXRlcyIsInNlc3Npb25fc3RhdGUiOiI0NTg2NTYzNi0yMjE4LTRhNDAtYWQyZS05M2RlMmJlZGJkM2IiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwic2lkIjoiNDU4NjU2MzYtMjIxOC00YTQwLWFkMmUtOTNkZTJiZWRiZDNiIn0.B8k6olblNpS6aU5mrQ7_62K1pPibwhvlboxoVi3ENrA",
  "token_type": "Bearer",
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJZUFB3M0l2MHQ5WHEzMW0zLUtCemgyaHk3Um1LSEJ5dEtIdWhHSWY4Vkw0In0.eyJleHAiOjE2NDkxNTQ3MzgsImlhdCI6MTY0OTE1MjkzOCwiYXV0aF90aW1lIjowLCJqdGkiOiIxMzJkYzU4Zi0wNWQ4LTQwNGUtOTkyZi1mMmVkMDU3Y2QyOTciLCJpc3MiOiJodHRwczovLzExLjguMzYuMjUvYXV0aC9yZWFsbXMvcHJvamVjdC0xIiwiYXVkIjoia3ViZXJuZXRlcyIsInN1YiI6IjA0ZWMwN2MzLWZmNjQtNGNkNS1hNzdlLTczOWU5ZTc5ZWMyYiIsInR5cCI6IklEIiwiYXpwIjoia3ViZXJuZXRlcyIsInNlc3Npb25fc3RhdGUiOiI0NTg2NTYzNi0yMjE4LTRhNDAtYWQyZS05M2RlMmJlZGJkM2IiLCJhdF9oYXNoIjoiWm5UVUtwYUxKRno2RHZTSlNEckZQUSIsImFjciI6IjEiLCJzaWQiOiI0NTg2NTYzNi0yMjE4LTRhNDAtYWQyZS05M2RlMmJlZGJkM2IiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJ0b20iLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ0b20ifQ.jDTGKWsvg-2z-01isqOpdHqiGSpiXxC3JKdgcVnBLx26xIEZdrjjsQxEXMd0yXJCqdiD4VNaQ6eHHJCjg3gyJE6_TT3XsxLafpBcfNb0N2TEdxQQxmwfUwK18SWAPFoUqd0ErhvZ_LelecOqytHOV2fOgkH58LCTbTP6mVvSsRuxo5Yp74scMLV-UWxi0ABT6NC3U5L_iiQBct_VAqQMxHu1Inv0RRYBA14L6AHtjNmhGoXTYakXqH_4PqZqlxt9rx-uINkRSlY0rV-eWyS-8xaOhKDu4zLWhJTgE_4YguNi2jXcd5ppM6p6uOzM48-az1flXpsPo8VUDgNsfrzg3A",
  "not-before-policy": 0,
  "session_state": "45865636-2218-4a40-ad2e-93de2bedbd3b",
  "scope": "openid profile email"
}
```

id_token 被编码为 JTW 格式的数据，将内容复制到 https://jwt.io/ 网站上可以看到 id_token 的内容，在 payload 部分中可以看到标识的用户信息：`name:tom`。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405181203.png)



请求 API Server 列出所有 namespace，在 curl 命令中使用 `-H` 参数将 id_token 附加到 HTTP 请求的 Header 中。
```bash
curl -k https://11.8.36.162:6443/api/v1/namespaces \
 -H "Authorization: Bearer <id_token>"
 
 # 返回结果
 {
  "kind": "NamespaceList",
  "apiVersion": "v1",
  "metadata": {
    "resourceVersion": "1120382"
  },
  "items": [
    {
      "metadata": {
        "name": "calico-apiserver",
        "uid": "3272d2ab-f842-4552-a87a-a9a7a14b3768",
        "resourceVersion": "1679",
        "creationTimestamp": "2022-03-29T02:21:45Z",
        "labels": {
          "kubernetes.io/metadata.name": "calico-apiserver",
          "name": "calico-apiserver"
        },
......
```

我们刚刚申请的令牌的有效期是 30 分钟，OAuth 2.0 允许用户自动更新令牌，在令牌到期之前，可以使用 refresh_token 发送一个请求，去更新令牌。
```bash
curl -ks -X POST https://11.8.36.25/auth/realms/project-1/protocol/openid-connect/token \
-d grant_type=refresh_token -d client_id=kubernetes \
-d client_secret=YsXXff8TL5EXNmSpTeDLdKf99cYBLqqq \
-d refresh_token=<refresh_token>"
```
Keycloak 服务器将会返回一个新的 access_token，id_token 和 refresh_token。
```bash
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJZUFB3M0l2MHQ5WHEzMW0zLUtCemgyaHk3Um1LSEJ5dEtIdWhHSWY4Vkw0In0.eyJleHAiOjE2NDkxNTUwOTksImlhdCI6MTY0OTE1MzI5OSwianRpIjoiNDUzZTU0MzctOGM0MC00NjA4LThmZmEtM2M5Nzc3MGU2MDczIiwiaXNzIjoiaHR0cHM6Ly8xMS44LjM2LjI1L2F1dGgvcmVhbG1zL3Byb2plY3QtMSIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiIwNGVjMDdjMy1mZjY0LTRjZDUtYTc3ZS03MzllOWU3OWVjMmIiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJrdWJlcm5ldGVzIiwic2Vzc2lvbl9zdGF0ZSI6IjQ1ODY1NjM2LTIyMTgtNGE0MC1hZDJlLTkzZGUyYmVkYmQzYiIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJkZWZhdWx0LXJvbGVzLXByb2plY3QtMSIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInNpZCI6IjQ1ODY1NjM2LTIyMTgtNGE0MC1hZDJlLTkzZGUyYmVkYmQzYiIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6InRvbSIsInByZWZlcnJlZF91c2VybmFtZSI6InRvbSJ9.DUm3Ju1mmZbl_tyKCMHfUnXTJQ3-M33rcQ3WuuX_7yhEQLK086mC4TZwi0chayBB72Ge6gX9exNkhl8FPMEbw41Qrr8wHsLev-cfJWq_jnnjVKXH3hvwIR-APr-YOjL0UUDAmIGW9FUi4iPOHSvinyyii4AHy_PT4L7OlYdnG3SWGs-0g5qbIl4Sm8vMYMz7bkIU0r7Vu7bxzPnflT3yzP6rTd3Ej6DsWkddSseaAbEOLeDW6pv_YBkhMH8gbcxGtVS5THnnfC--Qr9iIw7v1OFXH3olUFK5S9_vt99fsaHjruwAKUXoSS-BbzJFsJFnXnSFeRuXsIx6M95O94pb4w",
  "expires_in": 1800,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI3ZjMyMzBkNS0xNzZhLTQ1YjktOTUxNC0xZjBhY2JmODdhMzMifQ.eyJleHAiOjE2NDkxNTUwOTksImlhdCI6MTY0OTE1MzI5OSwianRpIjoiNmM2YTJmN2QtNzNlMi00MTY1LTg2MmEtZDU3YmJlYmMwNmU3IiwiaXNzIjoiaHR0cHM6Ly8xMS44LjM2LjI1L2F1dGgvcmVhbG1zL3Byb2plY3QtMSIsImF1ZCI6Imh0dHBzOi8vMTEuOC4zNi4yNS9hdXRoL3JlYWxtcy9wcm9qZWN0LTEiLCJzdWIiOiIwNGVjMDdjMy1mZjY0LTRjZDUtYTc3ZS03MzllOWU3OWVjMmIiLCJ0eXAiOiJSZWZyZXNoIiwiYXpwIjoia3ViZXJuZXRlcyIsInNlc3Npb25fc3RhdGUiOiI0NTg2NTYzNi0yMjE4LTRhNDAtYWQyZS05M2RlMmJlZGJkM2IiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwic2lkIjoiNDU4NjU2MzYtMjIxOC00YTQwLWFkMmUtOTNkZTJiZWRiZDNiIn0.N8jutxJkeEallahU5RdHkv4Lctgv8ojenuZFwrxDjPo",
  "token_type": "Bearer",
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJZUFB3M0l2MHQ5WHEzMW0zLUtCemgyaHk3Um1LSEJ5dEtIdWhHSWY4Vkw0In0.eyJleHAiOjE2NDkxNTUwOTksImlhdCI6MTY0OTE1MzI5OSwiYXV0aF90aW1lIjowLCJqdGkiOiIzYzljZmY2Ny01NGZlLTQ4MWItYjkwYy0xMmU4ODQwMGE3YmIiLCJpc3MiOiJodHRwczovLzExLjguMzYuMjUvYXV0aC9yZWFsbXMvcHJvamVjdC0xIiwiYXVkIjoia3ViZXJuZXRlcyIsInN1YiI6IjA0ZWMwN2MzLWZmNjQtNGNkNS1hNzdlLTczOWU5ZTc5ZWMyYiIsInR5cCI6IklEIiwiYXpwIjoia3ViZXJuZXRlcyIsInNlc3Npb25fc3RhdGUiOiI0NTg2NTYzNi0yMjE4LTRhNDAtYWQyZS05M2RlMmJlZGJkM2IiLCJhdF9oYXNoIjoiZHhfSDc2eFZEUUtseUd1Z2tHZlRlQSIsImFjciI6IjEiLCJzaWQiOiI0NTg2NTYzNi0yMjE4LTRhNDAtYWQyZS05M2RlMmJlZGJkM2IiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJ0b20iLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ0b20ifQ.IXnHePIhj7vjxPtENmTsv1PJ9xXrlowtMsR4akFblGEo__YYWs4GWY0aFOKGQTyFh6sVtGy7olOxEcHwgVRkp7Sfzeplx7o9Z-c5OYQORqmM0pX329oT9VfCBMMBX5ifIZPPfUlxZVLmygXUBk6LhnxD9MDzThEpHscoNnbHAODjSI2b_pTBOcLnr-inXl3klvaLi_Ti8SPCgd-cssd093DyvVK8Gb_UnpygtNVrailn-OU59wZu7wl-ah-pSqi9pAQTc3S4SJ_5aE722I23r6zxGwqghBxRKGqNS9vGcHsGgRfBHUQZOwa_w0cHyfvRfwVaqLn3_8JDrW-aCn3FuA",
  "not-before-policy": 0,
  "session_state": "45865636-2218-4a40-ad2e-93de2bedbd3b",
  "scope": "openid profile email"
}
```

## 9 用户访问资源

### 9.1 方式一：OIDC 身份认证组件
接下来使用以下命令在 kubeconfig 文件中为用户 tom 添加新的凭据，`idp-issuer-url` 参数的 URL 使用 **6.5 查看端点信息**章节中看到的 **issuer** 的地址。
```bash
kubectl config set-credentials tom \
   --auth-provider=oidc \
   --auth-provider-arg=idp-issuer-url=https://11.8.36.25/auth/realms/project-1 \
   --auth-provider-arg=client-id=kubernetes \
   --auth-provider-arg=client-secret=YsXXff8TL5EXNmSpTeDLdKf99cYBLqqq \
   --auth-provider-arg=refresh-token=<refresh_token> \
   --auth-provider-arg=id-token=<id_token> \
  --auth-provider-arg=idp-certificate-authority=/etc/kubernetes/pki/ca.crt
```

然后在 kubectl 命令中使用 `--user` 参数指定使用 tom 用户进行访问，可以看到该用户只有获取 namespace 的权限。
```bash
# 可以获取 namespace
$ kubectl --user tom get namespace
NAME               STATUS   AGE
calico-apiserver   Active   7d7h
calico-system      Active   7d8h
default            Active   7d8h
kube-node-lease    Active   7d8h
kube-public        Active   7d8h
kube-system        Active   7d8h
tigera-operator    Active   7d8h

# 没有获取 pod 的权限
$ kubectl --user tom get pod
Error from server (Forbidden): pods is forbidden: User "tom" cannot list resource "pods" in API group "" in the namespace "default"
```

我们可以为该用户添加上下文，方便在多集群/多用户的环境下进行切换。
```bash
kubectl config set-context tom --cluster=<集群名> --user=tom
```

查看 ~/.kube/config 文件可以看到为 tom 用户添加的凭据和上下文。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220406105056.png)

切换到用户 tom 进行访问。
```bash
# 切换用户上下文
kubectl config use-context tom
kubectl get namespaces
```


### 9.2 方式二：使用 --token 选项
`kubectl` 命令允许使用 `--token` 选项传递一个令牌。
```bash
kubectl get namespace --user tom --token=<id_token>
```

### 9.3 方式三：使用 Kubelogin
前面介绍的方式一和方式二有一个缺点，那就是在令牌过期后需要手动获取新的令牌，然后更新到 kubeconfig 文件或者 `--token` 参数中。好在社区提供了 kubelogin 插件可以解决这一繁琐的问题，kubelogin 是一个用于 Kubernetes OpenID Connect 进行身份认证的插件，也称为 kubectl oidc-login。当运行 kubectl 命令时，kubelogin 会打开浏览器，用户需要输入用户名和密码登录程序，认证通过后，kubelogin 会从认证服务器获取一个令牌，然后 kubectl 就可以使用该令牌和 API Server 进行通信，具体的流程图如下：

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220404205609.png)

kubelogin 插件支持不同的方式安装，包括 Homebrew，Krew，Chocolatey 等等。

```bash
# Homebrew (macOS and Linux)
brew install int128/kubelogin/kubelogin

# Krew (macOS, Linux, Windows and ARM)
kubectl krew install oidc-login

# Chocolatey (Windows)
choco install kubelogin
```

使用以下命令在 kubeconfig 文件中添加用户 tom 的凭证，`--insecure-skip-tls-verify` 参数表示忽略自签名证书不安全的风险。当用户 tom 执行 kubectl 命令时，将会通过 `kubectl oidc-login get-token` 命令获取令牌。
```bash
kubectl config set-credentials tom \
    --exec-api-version=client.authentication.k8s.io/v1beta1 \
    --exec-command=kubectl \
    --exec-arg=oidc-login \
    --exec-arg=get-token \
    --exec-arg=--oidc-issuer-url=https://11.8.36.25/auth/realms/project-1 \
    --exec-arg=--oidc-client-id=kubernetes \
    --exec-arg=--oidc-client-secret=YsXXff8TL5EXNmSpTeDLdKf99cYBLqqq \
    --exec-arg=--insecure-skip-tls-verify
```

有关 kubelogin 的详细参数参见：[kubelogin usage and options](https://github.com/int128/kubelogin/blob/master/docs/usage.md)。设置完毕后，使用 kubectl 命令访问时，浏览器会自动弹出 Keycloak 认证页面，输入用户名和密码后就可以正常访问相应的资源了。
```bash
kubectl --user=tom get namespace
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220405_192515_.gif)

kubelogin 的 id_token 和 refresh_token 缓存在 `~/.kube/cache/oidc-login/` 目录中，没有超过令牌有效期时，无需再次输入用户名和密码进行认证。

## 10 总结
本文通过详细的步骤为大家展示了如何让 API Server 使用 OpenID Connect 协议集成 Keycloak 进行身份认证，同时介绍了如何使用 kubectl 和 kubelogin 进行用户登录认证。

## 参考资料
- [利用Keycloak实现Kubernetes单点登录与权限验证（SSO,OIDC,RBAC）](https://www.jianshu.com/p/89eba92af52f)
- [kubectl with OpenID Connect](https://medium.com/@int128/kubectl-with-openid-connect-43120b451672)
- [使用 KeyCloak 对 Kubernetes 进行统一用户管理](https://cloud.tencent.com/developer/article/1804656)
- [kubelogin](https://github.com/int128/kubelogin)
- [Kubernetes OpenID Connection authentication](https://github.com/int128/kubelogin/blob/master/docs/setup.md)
- [Kubernetes auth Keycloak as identity provider](https://faun.pub/kubernetes-auth-e2f342a5f269)
- [如何在 Apache APISIX 中集成 Keycloak 实现身份认证](https://apisix.apache.org/zh/blog/2021/12/10/integrate-keycloak-auth-in-apisix/)
- [Configuring Keycloak for production](https://www.keycloak.org/server/configuration-production)
- [Keycloak with Quarkus: Better together](https://www.novatec-gmbh.de/en/blog/keycloak-with-quarkus-better-together/)
- [Keycloak Docker image](https://hub.docker.com/r/jboss/keycloak/)
- [How to authenticate user with Keycloak OIDC Provider in Kubernetes](https://middlewaretechnologies.in/2022/01/how-to-authenticate-user-with-keycloak-oidc-provider-in-kubernetes.html)
- [Keycloak access token expires too soon](https://stackoverflow.com/questions/62640241/keycloak-access-token-expires-too-soon)
- [How to Secure Your Kubernetes Cluster with OpenID Connect and RBAC](https://developer.okta.com/blog/2021/11/08/k8s-api-server-oidc)

## 欢迎关注
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220104221116.png)