# Mini NPU Simulator

파이썬 순수 반복문과 부동소수점 비교 정책을 활용한 미니 NPU(Neural Processing Unit) 시뮬레이터입니다. 본 프로젝트는 외부 라이브러리(NumPy 등) 없이 MAC(Multiply-Accumulate) 연산의 원리를 구현하고, 데이터 크기에 따른 연산 성능을 분석하는 것을 목표로 합니다.

---

## 1. 실행 방법 (How to Run)

### 환경 요구사항
- Python 3.8 이상 (외부 라이브러리 없음, 표준 라이브러리 `json`, `time`만 사용)

### 파일 배치
프로젝트 루트 폴더에 아래와 같은 구조로 파일이 위치해야 합니다.
```text
mini_npu_project/
│
├── src/
│   ├── __init__.py
│   ├── npu_core.py
│   └── simulator.py
│
├── data.json
├── main.py
└── README.md