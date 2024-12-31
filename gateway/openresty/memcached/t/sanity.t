use Test::Nginx::Socket::Lua::Stream;

run_tests();

__DATA__

=== TEST 1: basic get and set
--- config
        location /test {
            content_by_lua_block {
                local memcached = require "resty.memcached"
                local memc, err = memcached:new()
                if not memc then
                    ngx.say("failed to instantiate memc: ", err)
                    return
                end

                memc:set_timeout(1000) -- 1 sec
                local ok, err = memc:connect("127.0.0.1", 11212)

                local ok, err = memc:set("dog", 32)
                if not ok then
                    ngx.say("failed to set dog: ", err)
                    return
                end

                local res, flags, err = memc:get("dog")
                ngx.say("dog: ", res)
            }
        }

--- stream_config
    lua_shared_dict memcached 100m;

--- stream_server_config
    listen 11212;
    content_by_lua_block {
        local m = require("resty.memcached.server")
        m.go()
    }

--- request
GET /test
--- response_body
dog: 32
--- no_error_log
[error]