#include "threadpool.h"

ThreadPool::ThreadPool()
    :   _workers(),
        _taskQueue(),
        _taskCount( 0u ),
        _mutex(),
        _condition(),
        _stop( false ) {}

ThreadPool::ThreadPool( size_t threads ) : ThreadPool() {
    initializeWithThreads( threads );
}

ThreadPool::~ThreadPool() {
    _stop = true;
    _condition.notify_all();
    for ( std::thread& w: _workers ) {
        w.join();
    }
}

void ThreadPool::initializeWithThreads( size_t threads ) {
    for ( size_t i = 0; i < threads; i++ ) {
        // each thread executes this lambda
        _workers.emplace_back( [this]() -> void {
            while (true) {
                std::function<void()> task;
                {   // acquire lock
                    std::unique_lock<std::mutex> lock( _mutex );
                    _condition.wait( lock, [this]() -> bool {
                        return !_taskQueue.empty() || _stop;
                    });

                    if ( _stop && _taskQueue.empty() ) {
                        return;
                    }

                    task = std::move( _taskQueue.front() );
                    _taskQueue.pop();
                }   // release lock
                task();
                _taskCount--;
            }
        });
    }
}

void ThreadPool::schedule( const std::function<void()>& task ) {
    {
        std::unique_lock<std::mutex> lock( _mutex );
        _taskQueue.push( task );
    }
    _taskCount++;
    _condition.notify_one();
}

void ThreadPool::wait() const {
    while( _taskCount.load() > 0 ) {
        std::this_thread::yield();
    }
}