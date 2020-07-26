#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <atomic>
#include <condition_variable>
#include <functional>

class ThreadPool {
public:
    ThreadPool();
    ThreadPool( size_t threads );
    ~ThreadPool();

    void initializeWithThreads( size_t threads );

    void schedule( const std::function<void()>& );

    void wait() const;

private:
    std::vector<std::thread> _workers;
    std::queue<std::function<void()>> _taskQueue;
    std::atomic_uint _taskCount;
    std::mutex _mutex;
    std::condition_variable _condition;
    std::atomic_bool _stop;
};