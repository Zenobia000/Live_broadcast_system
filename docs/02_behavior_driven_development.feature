# 語言: zh-TW
Feature: 自動化出缺勤管理
  為了提升會議與活動的管理效率
  作為一名系統使用者
  我希望能有一個自動化、整合行事曆的簽到系統

  Background:
    Given "workspace.com" 網域中存在以下使用者:
      | name      | email              |
      | "陳大文"  | "damon@workspace.com" |
      | "管理員"  | "admin@workspace.com" |
    And 系統中存在一個預定的活動:
      | title          | start_time          | end_time            |
      | "每日站立會議" | "2025-10-14 09:00"  | "2025-10-14 09:15"  |

  @sprint-1 @core-feature @happy-path
  Scenario: 成員準時登入並自動簽到
    Given 現在時間是 "2025-10-14 09:01"
    When 使用者 "damon@workspace.com" 登入系統
    Then 系統應記錄 "damon@workspace.com" 在 "每日站立會議" 的狀態為 "出席"
    And "陳大文" 的儀表板上應顯示 "簽到成功" 的訊息

  @sprint-1 @core-feature @sad-path
  Scenario: 成員遲到登入
    Given 現在時間是 "2025-10-14 09:06"
    And 系統設定的遲到寬限時間為 5 分鐘
    When 使用者 "damon@workspace.com" 登入系統
    Then 系統應記錄 "damon@workspace.com" 在 "每日站立會議" 的狀態為 "遲到"
    And "陳大文" 的儀表板上應顯示 "您已遲到" 的訊息

  @sprint-2 @makeup-feature
  Scenario: 成員提交補簽申請
    Given "damon@workspace.com" 在 "每日站立會議" 的狀態為 "缺席"
    When "陳大文" 提交 "每日站立會議" 的補簽申請，理由為 "網路問題"
    Then 系統應建立一筆待審核的補簽記錄
    And 管理員 "admin@workspace.com" 應收到一則需要審核的通知

  @sprint-2 @leave-feature
  Scenario: 成員提交請假申請
    When "陳大文" 提交 "每日站立會議" 的請假申請，假別為 "病假"，理由為 "身體不適"
    Then 系統應記錄 "damon@workspace.com" 在 "每日站立會議" 的狀態為 "請假"
    And "每日站立會議" 在 Google Calendar 上的活動應更新，註記 "陳大文 (病假)"
    And 管理員 "admin@workspace.com" 應收到一則請假通知

  @sprint-2 @admin-feature
  Scenario: 管理員審核補簽申請
    Given 存在一筆來自 "damon@workspace.com" 關於 "每日站立會議" 的待審核補簽申請
    When 管理員 "admin@workspace.com" 批准該筆申請
    Then 系統應更新 "damon@workspace.com" 在 "每日站立會議" 的狀態為 "補簽"
    And "陳大文" 應收到一則 "補簽成功" 的通知

  @edge-case @idempotency
  Scenario: 成員在同一個活動期間重複登入
    Given 現在時間是 "2025-10-14 09:02"
    And 使用者 "damon@workspace.com" 已經在 "每日站立會議" 中被記錄為 "出席"
    When 使用者 "damon@workspace.com" 再次登入系統
    Then 系統中關於 "damon@workspace.com" 在 "每日站立會議" 的出席記錄應該只有一筆
    And "陳大文" 的儀表板不會顯示重複的簽到訊息

  @edge-case @sad-path
  Scenario: 成員在活動完全結束後才登入
    Given 現在時間是 "2025-10-14 09:30"
    When 使用者 "damon@workspace.com" 登入系統
    Then 系統不應該為 "每日站立會議" 創建任何新的簽到記錄
    And "陳大文" 的儀表板上應顯示 "目前沒有需要簽到的活動"

  @edge-case @conflict
  Scenario: 同時有多個時間重疊的活動
    Given 系統中存在另一個預定的活動:
      | title      | start_time          | end_time            |
      | "專案同步會議" | "2025-10-14 09:00"  | "2025-10-14 10:00"  |
    And 現在時間是 "2025-10-14 09:03"
    When 使用者 "damon@workspace.com" 登入系統
    Then 系統應記錄 "damon@workspace.com" 在 "每日站立會議" 的狀態為 "出席"
    And 系統應同時記錄 "damon@workspace.com" 在 "專案同步會議" 的狀態為 "出席"

  @sprint-2 @admin-feature @sad-path
  Scenario: 管理員拒絕補簽申請
    Given 存在一筆來自 "damon@workspace.com" 關於 "每日站立會議" 的待審核補簽申請
    When 管理員 "admin@workspace.com" 拒絕該筆申請，理由是 "理由不充分"
    Then 系統應更新 "damon@workspace.com" 在 "每日站立會議" 的狀態為 "缺席"
    And "陳大文" 應收到一則 "補簽申請被拒絕" 的通知，並看到拒絕理由

  @sprint-2 @conflict
  Scenario: 對已是「出席」狀態的活動申請補簽
    Given "damon@workspace.com" 在 "每日站立會議" 的狀態為 "出席"
    When "陳大文" 嘗試提交 "每日站立會議" 的補簽申請
    Then 系統應拒絕該申請，並提示 "您已出席，無需補簽"

  @sprint-2 @leave-feature @edge-case
  Scenario: 申請部分時間的請假 (例如：提早離開)
    Given 現在時間是 "2025-10-14 09:10"
    And "damon@workspace.com" 在 "每日站立會議" 的狀態為 "出席"
    When "陳大文" 提交請假申請，假別為 "事假"，時間為 "09:10" 到 "09:15"，理由為 "臨時約診"
    Then 系統應記錄 "damon@workspace.com" 在 "每日站立會議" 的狀態為 "提早離開"
    And 管理員 "admin@workspace.com" 應收到一則 "成員提早離開" 的通知
