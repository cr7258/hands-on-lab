use Test::Nginx::Socket 'no_plan';

run_tests;

__DATA__

=== TEST 1: max pool size is 200
--- http_config eval: $::HttpConfig
--- config
    location /t {
        content_by_lua_block {
          ngx.print("hello world")
        }
    }

--- request
GET /t

--- response_body chomp
hello world