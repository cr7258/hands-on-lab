local new_tab = require "table.new"
local str_sub = string.sub
local re_find = ngx.re.find
local mc_shdict = ngx.shared.memcached

local _M = { _VERSION = '0.01' }

local function parse_args(s, start)
    local arr = {}

    while true do
        local from, to = re_find(s, [[\S+]], "jo", {pos = start})
        if not from then
            break
        end

        table.insert(arr, str_sub(s, from, to))

        start = to + 1
    end

    return arr
end

function _M.get(tcpsock, keys)
    ngx.say("get")

    local reply = ""

    for i = 1, #keys do
        local key = keys[i]
        local value, flags = mc_shdict:get(key)
        if value then
            local flags  = flags or 0
            reply = reply .. "VALUE" .. key .. " " .. flags .. " " .. #value .. "\r\n" .. value .. "\r\n"
        end
    end
    reply = reply ..  "END\r\n"

    tcpsock:settimeout(1000)  -- one second timeout
    local bytes, err = tcpsock:send(reply)
end

function _M.set(tcpsock, res)
    ngx.say("set")

    local reply =  ""

    local key = res[1]
    local flags = res[2]
    local exptime = res[3]
    local bytes = res[4]

    local value, err = tcpsock:receive(tonumber(bytes) + 2)

    if str_sub(value, -2, -1) == "\r\n" then
        local succ, err, forcible = mc_shdict:set(key, str_sub(value, 1, bytes), exptime, flags)
        if succ then
            reply = reply .. "STORED\r\n"
        else
            reply = reply .. "SERVER_ERROR " .. err .. "\r\n"
        end
    else
        reply = reply .. "ERROR\r\n"
    end

    tcpsock:settimeout(1000)  -- one second timeout
    local bytes, err = tcpsock:send(reply)
end

function _M.run()
    local tcpsock = assert(ngx.req.socket(true))

    while true do
        tcpsock:settimeout(60000) -- 60 seconds
        local data, err = tcpsock:receive("*l")

        local command, args
        if data then
            local from, to, err = re_find(data, [[(\S+)]], "jo")
            if from then
                command = str_sub(data, from, to)
                args = parse_args(data, to + 1)
            end
        end

        if args then
            local args_len = #args
            if command == 'get' and args_len > 0 then
                _M.get(tcpsock, args)
            elseif command == "set" and args_len == 4 then
                _M.set(tcpsock, args)
            end
        end
    end
end

return _M