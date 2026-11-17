from src.simulator import run_mode_1, run_mode_2, run_performance_benchmark  # run_performance_benchmark 함수 추가 임포트

def main():
    while True:
        print("\n" + "="*40)
        print("=== Mini NPU Simulator ===")
        print("="*40)
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        print("3. 최적화 성능 비교 (보너스 과제)")  # <-- 보너스 메뉴 추가
        print("4. 종료")                             # <-- 번호 밀림 조정
        
        choice = input("선택 (1, 2, 3, 4): ").strip()  # <-- 입력 안내 수정
        
        if choice == "1":
            run_mode_1()
        elif choice == "2":
            run_mode_2()
        elif choice == "3":
            run_performance_benchmark()          # <-- 보너스 과제 함수 실행 연결
        elif choice == "4":
            print("\n프로그램을 종료합니다. 수고하셨습니다!")
            break
        else:
            print("\n[오류] 잘못된 입력입니다. 1, 2, 3, 4 중에 선택해주세요.")

if __name__ == "__main__":
    main()