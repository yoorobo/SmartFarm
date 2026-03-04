/**
 * PathFinder.h
 * ============
 * ESP32 로봇용 BFS 경로 탐색 모듈.
 *
 * 역할:
 *   - 16노드 그래프 기반 경로 탐색
 *   - BFS를 이용한 최단 경로 계산
 *   - calculatePath(startIdx, targetIdx, startDir) -> "LRUSE" + "E" 형식
 *
 * 방향: 0=N, 1=E, 2=S, 3=W
 * 명령: L=좌회전, R=우회전, U=U턴, S=직진, E=종료
 */

#ifndef PATH_FINDER_H
#define PATH_FINDER_H

#include <Arduino.h>

#define PATH_MAX_NODES 16
#define PATH_MAX_EDGES 6
#define PATH_STRING_MAX 64

/**
 * @brief 그래프 엣지 (인접 노드 + 출구 방향)
 */
struct PathEdge {
    int targetIdx;   // 연결된 노드 인덱스
    int exitDir;     // current 노드에서 나갈 때의 방향 (0~3)
};

/**
 * @brief 그래프 노드
 */
struct PathNode {
    const char* name;
    PathEdge edges[PATH_MAX_EDGES];
    int edgeCount;
};

/**
 * @brief BFS 경로 탐색 클래스
 */
class PathFinder {
public:
    PathFinder();

    /**
     * @brief 그래프 초기화. setup()에서 호출.
     */
    void initGraph();

    /**
     * @brief BFS로 최단 경로 계산.
     * @param startIdx     출발 노드 인덱스 (0~15)
     * @param targetIdx    목표 노드 인덱스 (0~15)
     * @param startDir     출발 시 바라보는 방향 (0~3)
     * @param outPath      출력: "LRUSE" 형식 문자열 (호출자가 버퍼 제공, PATH_STRING_MAX)
     * @param outNodeSeq   출력(선택): 경로상 노드 인덱스 배열 [start,...,target], 최대 PATH_MAX_NODES
     * @param maxNodes     outNodeSeq 크기
     * @return 경로 문자열 길이, 실패 시 -1
     */
    int calculatePath(int startIdx, int targetIdx, int startDir, char* outPath,
                     int* outNodeSeq = nullptr, int maxNodes = PATH_MAX_NODES);

    /**
     * @brief 노드 이름 -> 인덱스 변환.
     * @param nodeName 노드 이름 (예: "a01", "s06")
     * @return 0~15, 없으면 -1
     */
    int nodeNameToIndex(const char* nodeName) const;

    /**
     * @brief 인덱스 -> 노드 이름 변환.
     * @param idx 노드 인덱스 (0~15)
     * @return 노드 이름 포인터 (내부 배열)
     */
    const char* indexToNodeName(int idx) const;

    /**
     * @brief 전체 노드 수 반환.
     */
    int getNodeCount() const { return PATH_MAX_NODES; }

private:
    PathNode _nodes[PATH_MAX_NODES];
    bool _initialized;

    /**
     * @brief 방향 차이를 L/R/U/S 문자로 변환.
     * (targetDir - currentDir + 4) % 4 -> 0=S, 1=R, 2=U, 3=L
     */
    char dirDiffToChar(int currentDir, int targetDir) const;
};

#endif // PATH_FINDER_H
