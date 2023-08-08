duration=0
percentage=99
normal_requests=0
error_requests=0
endpoint=""

# 处理参数
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -d|--duration)
            duration="$2"
            shift
            shift
            ;;
        -p|--percentage)
            percentage="$2"
            shift
            shift
            ;;
        -e|--endpoint)
            endpoint="$2"
            shift
            shift
            ;;
        *)
            echo "未知的参数: $1"
            exit 1
            ;;
    esac
done

# 检查是否指定了必需的参数
if [[ -z "$endpoint" ]]; then
    echo "必须指定 -e 或 --endpoint 参数"
    exit 1
fi

# 定义退出处理函数
function on_exit {
    if [[ $? -eq 0 ]]; then
        echo "请求执行完毕"
    else
        echo "请求被中断"
    fi
    echo "正常请求: $normal_requests 次"
    echo "异常请求: $error_requests 次"
}

# 注册退出处理函数
trap on_exit EXIT

# 执行请求
start_time=$(date +%s)
while true; do
    if [[ "$duration" -gt 0 ]] && [[ $(date +%s) -gt $(($start_time + $duration)) ]]; then
        echo "达到指定的持续时间，脚本结束"
        break
    fi

    if (( $(echo "$percentage > $(echo "scale=6; $RANDOM/32767" | bc)" | bc -l) )); then
        curl -s "$endpoint" > /dev/null
        echo "执行正常请求"
        normal_requests=$((normal_requests + 1))
    else
        curl -s "$endpoint/err" > /dev/null
        echo "执行异常请求"
        error_requests=$((error_requests + 1))
    fi
done
