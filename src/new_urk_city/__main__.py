from .system import build_default_system


def main() -> None:
    system = build_default_system()
    result = system.run()
    print(result.daily_summary)
    print()
    print(result.weekly_report)
    print()
    print(result.action_queue)


if __name__ == "__main__":
    main()
