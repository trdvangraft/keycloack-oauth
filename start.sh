#! /usr/bin/env sh

# Runs the command, on non 0 status exits with the status
run_or_exit() {
  "$@"
  local status=$?
  if [ $status -ne 0 ]; then
    echo "❌ Error: '$*' failed with status $status" >&2
    exit $status
  fi
}


# Run migrations
# Start server
echo "🚀 Starting Uvicorn..."
exec uvicorn --factory src.todoist.app:create_app --host 0.0.0.0 --port 80 --reload --log-level debug
