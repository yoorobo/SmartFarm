/**
 * PathPlanner.cpp
 * ===============
 * 스마트팜 맵 그래프 기반 AGV 경로 탐색기 구현.
 */

#include "PathPlanner.h"

// ─────────── 노드 이름 테이블 ───────────
static const char* NODE_NAMES[NODE_COUNT] = {
    "입고장",   // 0  NODE_INBOUND
    "a01",     // 1  NODE_A01
    "a02",     // 2  NODE_A02
    "a03",     // 3  NODE_A03
    "a04",     // 4  NODE_A04
    "출고장",   // 5  NODE_OUTBOUND
    "s05",     // 6  NODE_S05
    "s06",     // 7  NODE_S06
    "s07",     // 8  NODE_S07
    "s11",     // 9  NODE_S11
    "s12",     // 10 NODE_S12
    "s13",     // 11 NODE_S13
    "r08",     // 12 NODE_R08
    "r09",     // 13 NODE_R09
    "r10",     // 14 NODE_R10
    "r14",     // 15 NODE_R14
    "r15",     // 16 NODE_R15
    "r16",     // 17 NODE_R16
};

// ============================================================
//  생성자
// ============================================================

PathPlanner::PathPlanner()
    : _currentNode(NODE_INBOUND)
    , _currentHeading(EAST)
{
    memset(_edgeCount, 0, sizeof(_edgeCount));
}

// ============================================================
//  맵 초기화
// ============================================================

void PathPlanner::addEdge(NodeId from, NodeId to, Direction dir) {
    int idx = _edgeCount[from];
    if (idx >= MAX_EDGES) return;
    _edges[from][idx] = {to, dir};
    _edgeCount[from]++;
}

void PathPlanner::initMap() {
    memset(_edgeCount, 0, sizeof(_edgeCount));

    // ── 메인 트랙 (E-W) ──
    // 입고장 ↔ a01
    addEdge(NODE_INBOUND, NODE_A01, EAST);
    addEdge(NODE_A01, NODE_INBOUND, WEST);

    // a01 ↔ a02
    addEdge(NODE_A01, NODE_A02, EAST);
    addEdge(NODE_A02, NODE_A01, WEST);

    // a02 ↔ a03
    addEdge(NODE_A02, NODE_A03, EAST);
    addEdge(NODE_A03, NODE_A02, WEST);

    // a03 ↔ a04
    addEdge(NODE_A03, NODE_A04, EAST);
    addEdge(NODE_A04, NODE_A03, WEST);

    // a04 ↔ 출고장
    addEdge(NODE_A04, NODE_OUTBOUND, EAST);
    addEdge(NODE_OUTBOUND, NODE_A04, WEST);

    // ── 상단 s구역 (a02 북쪽 분기) ──
    // a02 ↔ s06
    addEdge(NODE_A02, NODE_S06, NORTH);
    addEdge(NODE_S06, NODE_A02, SOUTH);

    // s05 ↔ s06 ↔ s07 (E-W)
    addEdge(NODE_S06, NODE_S05, WEST);
    addEdge(NODE_S05, NODE_S06, EAST);
    addEdge(NODE_S06, NODE_S07, EAST);
    addEdge(NODE_S07, NODE_S06, WEST);

    // s06 ↔ s12
    addEdge(NODE_S06, NODE_S12, NORTH);
    addEdge(NODE_S12, NODE_S06, SOUTH);

    // s11 ↔ s12 ↔ s13 (E-W)
    addEdge(NODE_S12, NODE_S11, WEST);
    addEdge(NODE_S11, NODE_S12, EAST);
    addEdge(NODE_S12, NODE_S13, EAST);
    addEdge(NODE_S13, NODE_S12, WEST);

    // s05 ↔ s11 (N-S)
    addEdge(NODE_S05, NODE_S11, NORTH);
    addEdge(NODE_S11, NODE_S05, SOUTH);

    // s07 ↔ s13 (N-S)
    addEdge(NODE_S07, NODE_S13, NORTH);
    addEdge(NODE_S13, NODE_S07, SOUTH);

    // ── 하단 r구역 (a03 남쪽 분기) ──
    // a03 ↔ r09
    addEdge(NODE_A03, NODE_R09, SOUTH);
    addEdge(NODE_R09, NODE_A03, NORTH);

    // r08 ↔ r09 ↔ r10 (E-W)
    addEdge(NODE_R09, NODE_R08, WEST);
    addEdge(NODE_R08, NODE_R09, EAST);
    addEdge(NODE_R09, NODE_R10, EAST);
    addEdge(NODE_R10, NODE_R09, WEST);

    // r09 ↔ r15
    addEdge(NODE_R09, NODE_R15, SOUTH);
    addEdge(NODE_R15, NODE_R09, NORTH);

    // r14 ↔ r15 ↔ r16 (E-W)
    addEdge(NODE_R15, NODE_R14, WEST);
    addEdge(NODE_R14, NODE_R15, EAST);
    addEdge(NODE_R15, NODE_R16, EAST);
    addEdge(NODE_R16, NODE_R15, WEST);

    // r08 ↔ r14 (N-S)
    addEdge(NODE_R08, NODE_R14, SOUTH);
    addEdge(NODE_R14, NODE_R08, NORTH);

    // r10 ↔ r16 (N-S)
    addEdge(NODE_R10, NODE_R16, SOUTH);
    addEdge(NODE_R16, NODE_R10, NORTH);

    Serial.printf("[PathPlanner] 맵 초기화 완료 (%d 노드)\n", NODE_COUNT);
}

// ============================================================
//  BFS 최단 경로
// ============================================================

bool PathPlanner::bfs(NodeId start, NodeId goal, NodeId parent[]) {
    bool visited[NODE_COUNT];
    memset(visited, false, sizeof(visited));
    for (int i = 0; i < NODE_COUNT; i++) parent[i] = (NodeId)-1;

    // 간단한 큐 (최대 NODE_COUNT)
    NodeId queue[NODE_COUNT];
    int front = 0, back = 0;

    visited[start] = true;
    queue[back++] = start;

    while (front < back) {
        NodeId curr = queue[front++];

        if (curr == goal) return true;

        for (int i = 0; i < _edgeCount[curr]; i++) {
            NodeId next = _edges[curr][i].to;
            if (!visited[next]) {
                visited[next] = true;
                parent[next] = curr;
                queue[back++] = next;
            }
        }
    }

    return false;  // 경로 없음
}

// ============================================================
//  방향 변환 → 회전 명령 생성
// ============================================================

void PathPlanner::appendTurns(Direction current, Direction target, String& out) {
    if (current == target) return;

    // 시계 방향 차이 계산 (0~3)
    int diff = ((int)target - (int)current + 4) % 4;

    switch (diff) {
        case 1:  // 우회전 90°
            out += '2';
            break;
        case 2:  // 180° → 우회전 2번
            out += '2';
            out += '2';
            break;
        case 3:  // 좌회전 90°
            out += '1';
            break;
    }
}

// ============================================================
//  경로 계획 (핵심 함수)
// ============================================================

String PathPlanner::planRoute(NodeId targetNode) {
    if (targetNode == _currentNode) {
        Serial.println("[PathPlanner] 이미 목적지에 있습니다.");
        return "5";  // 바로 도착
    }

    // 1. BFS로 최단 경로 탐색
    NodeId parent[NODE_COUNT];
    if (!bfs(_currentNode, targetNode, parent)) {
        Serial.println("[PathPlanner] ❌ 경로를 찾을 수 없습니다!");
        return "";
    }

    // 2. parent 배열로 경로 역추적
    NodeId path[NODE_COUNT];
    int pathLen = 0;
    for (NodeId n = targetNode; n != (NodeId)-1; n = parent[n]) {
        path[pathLen++] = n;
    }
    // 역순 → 정순
    for (int i = 0; i < pathLen / 2; i++) {
        NodeId tmp = path[i];
        path[i] = path[pathLen - 1 - i];
        path[pathLen - 1 - i] = tmp;
    }

    // 3. 경로 로그 출력
    Serial.print("[PathPlanner] 경로: ");
    for (int i = 0; i < pathLen; i++) {
        Serial.print(getNodeName(path[i]));
        if (i < pathLen - 1) Serial.print(" → ");
    }
    Serial.println();

    // 4. path 문자열 생성 (heading 고려)
    String result = "";
    Direction heading = _currentHeading;

    for (int i = 0; i < pathLen - 1; i++) {
        NodeId from = path[i];
        NodeId to   = path[i + 1];

        // 이 간선의 방향 찾기
        Direction edgeDir = NORTH;
        for (int e = 0; e < _edgeCount[from]; e++) {
            if (_edges[from][e].to == to) {
                edgeDir = _edges[from][e].dir;
                break;
            }
        }

        // 필요시 회전 명령 추가
        appendTurns(heading, edgeDir, result);
        heading = edgeDir;

        // 직진(교차로 통과) 명령 추가
        result += '4';
    }

    // 5. 종료 명령
    result += '5';

    // 도착 시 heading 저장 (onArrived에서 갱신)
    _currentHeading = heading;

    Serial.printf("[PathPlanner] 생성된 path: %s\n", result.c_str());
    return result;
}

// ============================================================
//  도착 처리
// ============================================================

void PathPlanner::onArrived(NodeId arrivedNode, Direction finalHeading) {
    _currentNode = arrivedNode;
    _currentHeading = finalHeading;
    Serial.printf("[PathPlanner] ✅ 도착! 현재 위치: %s, 방향: %d\n",
                  getNodeName(arrivedNode), finalHeading);
}

// ============================================================
//  유틸리티
// ============================================================

const char* PathPlanner::getNodeName(NodeId id) {
    if (id >= 0 && id < NODE_COUNT) return NODE_NAMES[id];
    return "UNKNOWN";
}

NodeId PathPlanner::findNodeByName(const char* name) {
    for (int i = 0; i < NODE_COUNT; i++) {
        if (strcmp(NODE_NAMES[i], name) == 0) {
            return (NodeId)i;
        }
    }
    return NODE_COUNT;  // 못 찾음
}
