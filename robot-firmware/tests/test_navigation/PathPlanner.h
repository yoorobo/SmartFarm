/**
 * PathPlanner.h
 * =============
 * 스마트팜 맵 그래프 기반 AGV 경로 탐색기.
 *
 * 역할:
 *   - 맵 노드/간선 그래프 정의 (20개 노드)
 *   - BFS 최단 경로 탐색
 *   - 현재 위치/방향 → 목적지까지 LineFollower용 path 문자열 생성
 *   - 현재 위치/방향 상태 추적
 *
 * 맵 구조:
 *              s11 ── s12 ── s13
 *               │      │      │
 *              s05 ── s06 ── s07
 *                      │
 *   입고장 ── a01 ── a02 ── a03 ── a04 ── 출고장
 *                      │
 *              r08 ── r09 ── r10
 *               │      │      │
 *              r14 ── r15 ── r16
 */

#ifndef PATH_PLANNER_H
#define PATH_PLANNER_H

#include <Arduino.h>

// ─────────── 방향 ───────────
enum Direction {
    NORTH = 0,
    EAST  = 1,
    SOUTH = 2,
    WEST  = 3
};

// ─────────── 노드 ID 상수 ───────────
// 인덱스로 사용 (0~19)
enum NodeId {
    NODE_INBOUND  = 0,   // 입고장
    NODE_A01      = 1,
    NODE_A02      = 2,
    NODE_A03      = 3,
    NODE_A04      = 4,
    NODE_OUTBOUND = 5,   // 출고장
    NODE_S05      = 6,
    NODE_S06      = 7,
    NODE_S07      = 8,
    NODE_S11      = 9,
    NODE_S12      = 10,
    NODE_S13      = 11,
    NODE_R08      = 12,
    NODE_R09      = 13,
    NODE_R10      = 14,
    NODE_R14      = 15,
    NODE_R15      = 16,
    NODE_R16      = 17,
    NODE_COUNT    = 18   // 총 노드 수
};

// ─────────── 간선 (방향 포함) ───────────
struct Edge {
    NodeId    to;
    Direction dir;   // 이 간선을 타려면 바라봐야 할 방향
};

// 노드당 최대 연결 수
#define MAX_EDGES 4

// ─────────── PathPlanner 클래스 ───────────
class PathPlanner {
public:
    PathPlanner();

    /**
     * @brief 맵 그래프 초기화. setup()에서 호출.
     */
    void initMap();

    /**
     * @brief 현재 위치에서 목적지까지의 LineFollower path 문자열 생성.
     * @param targetNode 목적지 노드 인덱스
     * @return path 문자열 (예: "41411245"), 실패 시 빈 문자열
     */
    String planRoute(NodeId targetNode);

    /**
     * @brief 도착 시 호출. 현재 위치/방향을 갱신한다.
     * @param arrivedNode  도착한 노드
     * @param finalHeading 도착 시 바라보는 방향
     */
    void onArrived(NodeId arrivedNode, Direction finalHeading);

    // ─────────── 상태 조회 ───────────
    NodeId    getCurrentNode()    const { return _currentNode; }
    Direction getCurrentHeading() const { return _currentHeading; }

    /**
     * @brief 노드 이름 문자열 반환 (디버깅/로그용).
     */
    static const char* getNodeName(NodeId id);

    /**
     * @brief 노드 이름 문자열로 NodeId 검색.
     * @return 찾으면 해당 NodeId, 못 찾으면 NODE_COUNT
     */
    static NodeId findNodeByName(const char* name);

private:
    // ─────────── 그래프 ───────────
    Edge _edges[NODE_COUNT][MAX_EDGES];
    int  _edgeCount[NODE_COUNT];

    void addEdge(NodeId from, NodeId to, Direction dir);

    // ─────────── BFS ───────────
    bool bfs(NodeId start, NodeId goal, NodeId parent[]);

    // ─────────── 방향 → 회전 변환 ───────────
    /**
     * @brief 현재 heading에서 target 방향으로 가려면 어떤 회전이 필요한지 계산.
     * @param current 현재 방향
     * @param target  가고 싶은 방향
     * @param out     path 문자열에 회전 명령 추가
     */
    void appendTurns(Direction current, Direction target, String& out);

    // ─────────── 현재 상태 ───────────
    NodeId    _currentNode;
    Direction _currentHeading;
};

#endif // PATH_PLANNER_H
