#ifndef SERVO_ARM_CONTROLLER_H
#define SERVO_ARM_CONTROLLER_H

#include <Arduino.h>
#include <ESP32Servo.h>

/**
 * @class ServoArmController
 * @brief 17번(360도 연속 회전 팔) 및 16번(180도 그리퍼) 서보모터 제어 클래스
 *
 * 360도 연속회전 서보 제어 방식 (write 기준):
 *   write(90)  = 정지
 *   write(0)   = 시계방향 회전
 *   write(180) = 반시계방향 회전
 *
 * @note MOVE_TIME_HALF을 조정하여 반 바퀴(180도) 회전량을 맞추세요.
 */
class ServoArmController {
private:
    Servo _armServo;
    Servo _gripperServo;
    bool _armEnabled = false;

    // 핀 번호 설정
    const int PIN_ARM = 17;
    const int PIN_GRIPPER = 16;

    // 360도 연속회전 모터 제어값
    const int MOTOR_STOP = 90;
    const int DIR_CW = 0;             // 시계방향
    const int DIR_CCW = 180;          // 반시계방향

    // 반 바퀴(180도) 회전 시간 (ms) - 기구 부하에 따라 조정
    const int MOVE_TIME_HALF = 780;
    const int MOVE_TIME_FULL = 0;

    // 180도 그리퍼 제어값
    const int GRIPPER_OPEN = 55;      // 놓기
    const int GRIPPER_CLOSE = 180;    // 잡기

    /**
     * @brief 암 서보를 안전하게 attach (즉시 정지 신호 보낸 후 안정화)
     */
    void armAttach() {
        _armServo.attach(PIN_ARM, 500, 2400);
        _armServo.write(MOTOR_STOP);  // attach 직후 즉시 정지!
        delay(200);                    // 안정화 대기
    }

    /**
     * @brief 암 서보를 안전하게 detach (정지 후 해제)
     */
    void armDetach() {
        _armServo.write(MOTOR_STOP);
        delay(100);
        _armServo.detach();
    }

public:
    ServoArmController() {}

    void setArmEnabled(bool enabled) { _armEnabled = enabled; }
    bool isArmEnabled() const { return _armEnabled; }

    void init() {
        if (!_armEnabled) {
            Serial.println("[ServoArmController] 초기화 생략 (arm 비활성화)");
            return;
        }
        ESP32PWM::allocateTimer(0);
        ESP32PWM::allocateTimer(1);
        
        // 핀17, 핀16 모두 초기화 시 attach 하지 않음!
        // 웹 버튼 명령이 올 때만 attach → 동작 → detach
        _armServo.setPeriodHertz(50);
        _gripperServo.setPeriodHertz(50);
        
        Serial.println("[ServoArmController] 초기화 완료 (핀17/16 모두 명령 시에만 동작)");
    }

    // ===================================================
    // 암 모터 (360도 연속회전) 제어 함수
    // ===================================================

    void rotateArmCW() {
        if (!_armEnabled) return;
        Serial.println(" -> [동작] 암 시계방향 회전");
        armAttach();
        _armServo.write(DIR_CW);
        delay(MOVE_TIME_FULL);
        armDetach();
        Serial.println(" -> 암 시계방향 완료!");
    }

    void rotateArmCCW() {
        if (!_armEnabled) return;
        Serial.println(" -> [동작] 암 반시계방향 회전");
        armAttach();
        _armServo.write(DIR_CCW);
        delay(MOVE_TIME_FULL);
        armDetach();
        Serial.println(" -> 암 반시계방향 완료!");
    }

    void rotateArm180CW() {
        if (!_armEnabled) return;
        Serial.println(" -> [동작] 암 시계방향 180도");
        armAttach();
        _armServo.write(DIR_CW);
        delay(MOVE_TIME_HALF);
        armDetach();
        Serial.println(" -> 암 180도 완료!");
    }

    void rotateArm180CCW() {
        if (!_armEnabled) return;
        Serial.println(" -> [동작] 암 반시계방향 180도");
        armAttach();
        _armServo.write(DIR_CCW);
        delay(MOVE_TIME_HALF);
        armDetach();
        Serial.println(" -> 암 180도 완료!");
    }

    // ===================================================
    // 그리퍼 (180도 서보) 제어 함수
    // ===================================================

    void grabGripper() {
        if (!_armEnabled) return;
        Serial.println(" -> [동작] 그리퍼 잡기");
        _gripperServo.attach(PIN_GRIPPER, 500, 2400);
        delay(50);
        _gripperServo.write(GRIPPER_CLOSE); 
        delay(500);
        _gripperServo.detach();
    }

    void releaseGripper() {
        if (!_armEnabled) return;
        Serial.println(" -> [동작] 그리퍼 놓기");
        _gripperServo.attach(PIN_GRIPPER, 500, 2400);
        delay(50);
        _gripperServo.write(GRIPPER_OPEN); 
        delay(500);
        _gripperServo.detach();
    }

    // ===================================================
    // 매크로 동작 함수
    // ===================================================

    void pickReady() {
        if (!_armEnabled) { Serial.println("[ServoArm] 픽업 준비 (비활성화)"); return; }
        Serial.println("[ServoArm] 픽업 준비: 그리퍼 열기 -> 팔 내리기");
        releaseGripper();
        rotateArmCW();
        delay(500);
    }

    void pickExecute() {
        if (!_armEnabled) { Serial.println("[ServoArm] 픽업 실행 (비활성화)"); return; }
        Serial.println("[ServoArm] 픽업 실행: 그리퍼 닫기 -> 팔 올리기");
        grabGripper();
        delay(500);
        rotateArmCCW();
        Serial.println("[ServoArm] 픽업 적재 완료!");
    }

    void dropPot() {
        if (!_armEnabled) { Serial.println("[ServoArm] 내려놓기 (비활성화)"); return; }
        Serial.println("[ServoArm] 내려놓기 시작");
        rotateArmCW();
        delay(500);
        releaseGripper();
        delay(500);
        rotateArmCCW();
        Serial.println("[ServoArm] 내려놓기 완료!");
    }
};

#endif // SERVO_ARM_CONTROLLER_H
