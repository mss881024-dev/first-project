# 전자서명 3rd Party 벤더 비교: 모두싸인 vs 도큐사인
Law.ai SaaS 연동 관점 / 국내 본인인증·비용·범용성 중심 임원 보고 자료

---

## 자료 조사 방법 및 한계 (원칙 고지)

- 본 자료는 사실(fact)만 기술하며, 의견·추측·마케팅 문구·과장 표현을 배제한다.
- 확인 불가 항목은 "공식 확인 불가"로 표기한다.
- 출처는 항목별로 표기하며, 공식 1차 출처를 우선하고, 파트너·블로그·경쟁사 자료는 보조 근거로만 사용하고 편향 가능성을 표시한다.
- **조사 제약**: 도큐사인 공식 요금제 페이지(ecom.docusign.com), 도큐사인 공식 가격 페이지(docusign.com/pricing), 모두싸인 공식 페이지(modusign.co.kr/pricing, modusign.co.kr/identify) 등 일부 공식 페이지는 자동 조사 도구의 직접 접속이 차단(HTTP 403)되어, 검색 엔진이 색인한 페이지 콘텐츠 스니펫 및 3차 자료 교차 확인을 통해 수치를 정리했다. 임원 보고 확정 전 각 공식 URL 직접 접속을 통한 재확인을 권고한다.

---

## 슬라이드 1. 표지

- **제목**: 전자서명 3rd Party 벤더 비교: 모두싸인 vs 도큐사인
- **부제**: Law.ai SaaS 연동 관점 / 국내 본인인증·비용·범용성 중심
- **작성일**: 2026-07-02

---

## 슬라이드 2. 결론 요약

| 판단 기준 | 결론 | 근거(요약) |
|---|---|---|
| 국내 본인인증이 핵심인 경우 | 모두싸인이 관련 기능을 공식 지원함이 확인됨 | 모두싸인은 통신사 기반 휴대폰 본인인증(SKT/KT/LGU+/알뜰통신사 명의 대조)과 법인 공동인증서 인증을 공식 지원 문서에 명시. 도큐사인은 동일 기능에 대한 공식 지원 여부가 확인되지 않음 |
| 해외/글로벌 계약이 많은 경우 | 도큐사인이 관련 기능을 공식 지원함이 확인됨 | 도큐사인은 188개국 대상 전자서명 적법성 가이드, 서명자 인터페이스 43개 언어를 공식 문서에 명시. 모두싸인은 인터페이스 다국어(한/영/중/일/베) 지원은 확인되나 국가별 적법성 가이드는 공식 확인 불가 |
| 비용 초과 과금 단가의 명확성 | 모두싸인은 초과 건당 단가가 공개됨, 도큐사인은 초과 과금 방식만 확인되고 단가는 공식 확인 불가 | 모두싸인: 초과 시 건당 1,900원 충전 방식 명시. 도큐사인: Pay-As-You-Go 방식으로 초과 Envelope 과금한다고 명시되어 있으나, 구체 단가는 공식 확인 불가 |
| API 연동 관점의 별도 계약 전제 | 도큐사인은 eSignature 요금제와 분리된 별도 Developer/API 과금 체계가 존재함, 모두싸인은 API 연동이 Team Pro 요금제에 포함되는 구조로 확인됨 | 도큐사인 Developer Plans는 API 기능·Envelope 볼륨 기준 별도 과금. 모두싸인은 가입 단계에서 'Team Pro + API 연동' 옵션으로 제공되는 구조 |

※ 위 결론은 모두 아래 슬라이드의 개별 출처에 근거하며, 상대적 우열("더 좋다")이 아닌 "공식 확인된 지원 여부"만을 기술함.

---

## 슬라이드 3. 국내 본인인증 지원 비교

| 인증 수단 | 모두싸인 | 도큐사인 |
|---|---|---|
| 카카오 인증 | 미지원 | 공식 확인 불가 |
| 네이버 인증 | 미지원 | 공식 확인 불가 |
| 토스 인증 | 미지원 | 공식 확인 불가 |
| PASS / 휴대폰 본인인증(통신사 명의 대조 방식) | 지원 | 미지원(단, 전화번호 소유 확인용 SMS/전화 OTP 인증은 별도로 존재) |
| 법인 공동인증서 | 지원(PC 환경 한정) | 공식 확인 불가 |
| 이메일/휴대폰 기반 인증 | 지원 | 지원 |

**주석**
- 모두싸인의 기본 인증은 이메일·휴대폰 알림 수신 확인이며, 카카오톡은 서명 요청 "알림 전송 채널"로만 사용되고 별도의 카카오 계정 기반 인증 수단으로는 지원 문서에 등재되어 있지 않음.
- 모두싸인 공식 지원 문서(추가 인증 수단 설정 방법)에 명시된 인증 수단은 휴대폰 본인인증, 접근암호 인증, 법인 공동인증서 인증 3종이며, 카카오·네이버·토스 인증서는 목록에 없음.
- 도큐사인 Phone Authentication은 전화·문자로 발송되는 인증코드 입력 방식(OTP)으로, 통신사 명의와 대조하는 한국형 PASS/휴대폰 본인인증과는 방식이 다름.

**출처**
- [공식1차] https://support.modusign.co.kr/ko/articles/%EC%B6%94%EA%B0%80-%EC%9D%B8%EC%A6%9D-%EC%88%98%EB%8B%A8-%EC%84%A4%EC%A0%95-%EB%B0%A9%EB%B2%95-c72016f0 (추가 인증 수단 설정 방법)
- [공식1차] https://modusign.co.kr/identify (모두싸인 본인/위변조 확인)
- [공식1차] https://developers.docusign.com/docs/esign-rest-api/esign101/concepts/recipients/auth/ (Recipient Authentication)
- [공식1차] https://www.docusign.com/products/identify/phone-authentication (Phone Authentication)
- [공식1차] https://support.docusign.com/en/guides/What-countries-is-ID-Verification-available-in (ID Verification 대상국)

---

## 슬라이드 4. 비용 구조 비교

| 항목 | 모두싸인 | 도큐사인 |
|---|---|---|
| 개인용 요금제 | Personal, 월 결제만 가능, 월 5건 서명 요청 제공. 정확한 월 구독료는 공식 확인 불가(검색 스니펫에서 수치 미확보) | Personal, 월 $15 / 연간 결제 시 월 $10 환산, 월 5 Envelope 제공(3차 자료 교차 확인, 공식 페이지 직접 확인 권고) |
| 팀/조직용 요금제 | Team: 월 39,900원, 최대 3인, 월 30건 제공. Team Pro: 최대 10인, 월 30건 제공, 정확한 구독료는 공식 확인 불가 | Standard: 월 $45 / 연간 결제 시 월 $25 환산, 연 100 Envelope/user. Business Pro: 월 $65 / 연간 결제 시 월 $40 환산, 연 100 Envelope/user(3차 자료 교차 확인) |
| 좌석당 과금 여부 | 공식 확인 불가(Team/Team Pro는 이용 인원 상한만 확인되며 좌석당 단가 정보는 미확인) | 지원(user 단위 과금 명시) |
| 서명 건수(Envelope/요청건) 제한 | Personal 월 5건, Team·Team Pro 월 30건. 잔여 건수는 이월되지 않고 소멸 | Standard·Business Pro: 연간 결제 시 연 100건/user, 월간 결제 시 월 10건/user |
| 초과 과금 방식 | 건당 1,900원 추가 충전 | Pay-As-You-Go 방식으로 초과 Envelope당 정액 과금. 구체 단가는 공식 확인 불가 |
| 맞춤형/Enterprise 견적 방식 | 연간 예상 이용량 약 1,000건 이상 시 별도 상담(맞춤형 요금제) | Advanced Solutions / IAM 등 상위 상품은 별도 영업 상담. 구체 산정 기준은 공식 확인 불가 |
| 다이렉트 구매 가능 여부 vs 영업 상담 필수 여부 | Personal/Team/Team Pro는 온라인 자체 결제 가능. 맞춤형(Enterprise급)은 상담 필요 | Personal/Standard/Business Pro는 온라인 자체 결제 가능(ecom.docusign.com). Advanced Solutions/IAM 등은 영업 상담 필요 |

**주석**
- 모두싸인은 원화(KRW), 도큐사인은 달러(USD) 기준으로 통화 단위가 다르며, 환율에 따른 직접 비교 시 별도 환산이 필요함.
- 도큐사인 표준 요금제 수치는 공식 페이지(ecom.docusign.com/plans-and-pricing/esignature) 직접 접속이 차단되어 검색 색인 스니펫 및 3차 자료로 교차 확인한 값으로, 임원 보고 확정 전 공식 페이지 재확인 필요.

**출처**
- [공식1차] https://modusign.co.kr/pricing (모두싸인 요금 안내)
- [공식1차] https://support.modusign.co.kr/ko/articles/%EC%9A%94%EA%B8%88%EC%A0%9C-%EC%95%88%EB%82%B4-8a0f022c (요금제 안내)
- [공식1차] https://ecom.docusign.com/plans-and-pricing/esignature (직접 접속 차단, 검색 색인 기준 교차 확인)
- [공식1차] https://support.docusign.com/s/articles/Docusign-Plans-and-Limits (Envelope 한도 공식 문서)
- [독립3rd] https://www.vendr.com/marketplace/docusign (SaaS 구매 중개 플랫폼)
- [경쟁사] https://eversign.com/blog/docusign-pricing-plans-cost-alternatives (경쟁 e서명 서비스, 가격 왜곡 가능성 있음)
- [경쟁사] https://www.pandadoc.com/blog/docusign-pricing/ (경쟁 서비스)

---

## 슬라이드 5. 범용성 비교

| 항목 | 모두싸인 | 도큐사인 |
|---|---|---|
| 지원 언어 | 인터페이스 기준 한국어 + 영어 + 중국어 + 일본어 + 베트남어(계약 문서 내용 자동번역 아님, 인터페이스만 다국어) | 서명자(Signer) 인터페이스 43개 언어, 문서 발송(Sender) 인터페이스 13개 언어(한국어 포함) |
| 지원 국가/지역 | 공식 확인 불가(글로벌 서비스 대상 국가 목록에 대한 공식 1차 자료 미확인) | 전자서명 적법성 가이드 기준 188개국에서 이용 중이라고 명시 |
| 해외 계약 시 약관/책임 소재 | 공식 확인 불가 | EU eIDAS 및 EU 전자서명 기술표준 준수를 명시(EU 범위 한정). 국가별 법적 효력은 현지 법무법인 분석에 기반한 자체 Legality Guide로 제공 |
| 글로벌 고객사/채택 범위 | 공식 확인 불가 | 공식 확인 불가(검증 가능한 1차 자료 기준의 구체 고객사 수·채택 통계 미확인) |
| 국내 사용성 vs 해외 사용성 | 국내향: 통신사 기반 휴대폰 본인인증·법인 공동인증서 지원 확인. 해외향: 인터페이스 다국어(5개 언어) 지원 확인 | 국내향: 카카오·네이버·토스 등 국내 간편인증 지원은 공식 확인 불가. 해외향: Phone/ID Verification 인프라가 다수 국가 대상으로 명시됨 |

**출처**
- [공식1차] https://blog.modusign.co.kr/news/update_multilingual_support (다국어 지원 - 영어)
- [공식1차] https://blog.modusign.co.kr/news/update/foreign-language (다국어 확장 - 중국어/일본어/베트남어)
- [공식1차] https://support.docusign.com/guides/ndse-user-guide-supported-languages (지원 언어 목록)
- [공식1차] https://support.docusign.com/s/articles/Is-DocuSign-Legal-in-my-Country (전자서명 적법성 가이드, 188개국)
- [공식1차] https://www.docusign.com/products/identify/phone-authentication (Phone Authentication 국가·언어 범위)

---

## 슬라이드 6. API/연동 비교

| 항목 | 모두싸인 | 도큐사인 |
|---|---|---|
| API 연동 방식 | REST API, Basic 인증 스킴, Webhook(이벤트 발생 시 지정 URL로 POST) 지원 | eSignature REST API |
| 별도 개발 필요 여부 | 필요(API 연동 시 자체 개발 필요) | 필요(API 연동 시 자체 개발 필요) |
| SaaS 내장형 연동 가능 여부 | 임베디드 서명요청/문서열람 링크 생성 기능 제공 | PowerForms 등 코드 최소화 연동 옵션이 개발자 문서에 존재(세부 사항은 공식 확인 불가 수준으로, 개발자 문서 직접 확인 권고) |
| API 전용 과금 체계 유무 | Team Pro 이상 요금제에 API 연동이 포함되는 구조로 확인됨(별도의 API 전용 단가 체계는 공식 확인 불가) | 존재. Developer Plans는 API 기능 및 Envelope 발송 볼륨 기준으로 별도 과금 |
| eSignature 요금제와 분리된 별도 API 라이선스 존재 여부 | 미분리(가입 시 'Team Pro + API 연동' 옵션으로 제공) | 분리 존재(Production 환경 이전 시 Developer Plan으로 별도 계약) |

**출처**
- [공식1차] https://developers.modusign.co.kr/docs/api-%EC%86%8C%EA%B0%9C (API 소개)
- [공식1차] https://developers.modusign.co.kr/docs/api-key-%EB%B0%9C%EA%B8%89 (API KEY 발급)
- [공식1차] https://developers.docusign.com/docs/esign-rest-api/esign101/ (eSignature REST API 101)
- [공식1차] https://ecom.docusign.com/plans-and-pricing/developer (Developer Plans)

---

## 슬라이드 7. 법무팀 관점 추천 문구

- 국내 서명자 UX 및 국내 본인인증(휴대폰 통신사 명의인증, 법인 공동인증서)이 최우선이면, 해당 기능이 공식 지원 문서에 확인된 모두싸인이 검토 대상에 포함됨.
- 해외 거래처·글로벌 범용성(서명자 인터페이스 43개 언어, 188개국 적법성 가이드)이 최우선이면, 해당 기능이 공식 문서에 확인된 도큐사인이 검토 대상에 포함됨.
- 법무관리시스템(Law.ai SaaS) 연동 관점에서는, 도큐사인이 eSignature 요금제와 분리된 별도 Developer/API 과금 체계를 운영하고 있어 연동 시 별도 계약·예산 검토가 필요하며, 모두싸인은 API 연동이 Team Pro 요금제에 포함되는 구조로 확인됨.

---

## 슬라이드 8. 공식 확인 불가 항목 모음

| 영역 | 항목 | 대상 |
|---|---|---|
| 본인인증 | 카카오/네이버/토스 인증 지원 여부 | 도큐사인 |
| 본인인증 | 법인 공동인증서 지원 여부 | 도큐사인 |
| 비용 구조 | 개인용(Personal) 요금제 정확한 구독료 | 모두싸인 |
| 비용 구조 | Team Pro 요금제 정확한 구독료 | 모두싸인 |
| 비용 구조 | 좌석당 과금 단가 | 모두싸인 |
| 비용 구조 | 초과 Envelope 과금 단가 | 도큐사인 |
| 비용 구조 | Advanced Solutions/IAM 등 Enterprise 견적 산정 기준 | 도큐사인 |
| 범용성 | 서비스 대상 국가/지역 목록 | 모두싸인 |
| 범용성 | 해외 계약 시 약관/책임 소재(EU 외 지역) | 모두싸인 |
| 범용성 | 글로벌 고객사/채택 범위 통계 | 모두싸인, 도큐사인 공통 |
| API/연동 | API 전용 과금 단가 체계 상세 | 모두싸인 |
| API/연동 | SaaS 내장형(코드리스) 연동 기능 상세 | 도큐사인 |

---

## 1페이지 요약 대조표

| 비교 기준 | 모두싸인 | 도큐사인 |
|---|---|---|
| 국내 본인인증(카카오/네이버/토스) | 미지원 | 공식 확인 불가 |
| PASS/휴대폰 본인인증(통신사 명의 대조) | 지원 | 미지원(전화 OTP 인증은 별도 존재) |
| 법인 공동인증서 | 지원(PC 한정) | 공식 확인 불가 |
| 표준 요금제 결제 방식 | 정액 구독(월 39,900원~, 원화) + 초과 건당 1,900원 | 정액 구독(월 $15~$65, 달러) + 초과 Pay-As-You-Go(단가 비공개) |
| 좌석당 과금 | 공식 확인 불가 | 지원 |
| Enterprise 견적 | 영업 상담 필요 | 영업 상담 필요 |
| 지원 언어(인터페이스) | 5개 언어(한/영/중/일/베) | 서명자 43개 언어 / 발송자 13개 언어 |
| 서비스 적법성 공식 커버리지 | 공식 확인 불가 | 188개국 |
| API 연동 방식 | REST API + Webhook, Team Pro 요금제 포함형 | REST API, eSignature 요금제와 분리된 Developer Plan |
| API 전용 별도 과금 체계 | 공식 확인 불가(요금제 포함형으로 확인) | 존재 |

---

### 전체 출처 목록

**모두싸인 [공식1차]**
- https://modusign.co.kr/pricing
- https://modusign.co.kr/identify
- https://support.modusign.co.kr/ko/articles/%EC%9A%94%EA%B8%88%EC%A0%9C-%EC%95%88%EB%82%B4-8a0f022c
- https://support.modusign.co.kr/ko/articles/%EC%B6%94%EA%B0%80-%EC%9D%B8%EC%A6%9D-%EC%88%98%EB%8B%A8-%EC%84%A4%EC%A0%95-%EB%B0%A9%EB%B2%95-c72016f0
- https://developers.modusign.co.kr/docs/api-%EC%86%8C%EA%B0%9C
- https://developers.modusign.co.kr/docs/api-key-%EB%B0%9C%EA%B8%89
- https://blog.modusign.co.kr/news/update_multilingual_support
- https://blog.modusign.co.kr/news/update/foreign-language

**도큐사인 [공식1차]**
- https://ecom.docusign.com/plans-and-pricing/esignature
- https://ecom.docusign.com/plans-and-pricing/developer
- https://support.docusign.com/s/articles/Docusign-Plans-and-Limits
- https://developers.docusign.com/docs/esign-rest-api/esign101/concepts/recipients/auth/
- https://www.docusign.com/products/identify/phone-authentication
- https://support.docusign.com/en/guides/What-countries-is-ID-Verification-available-in
- https://support.docusign.com/guides/ndse-user-guide-supported-languages
- https://support.docusign.com/s/articles/Is-DocuSign-Legal-in-my-Country

**보조 자료(편향 가능성 있음, 참고용)**
- [독립3rd] https://www.vendr.com/marketplace/docusign
- [경쟁사] https://eversign.com/blog/docusign-pricing-plans-cost-alternatives
- [경쟁사] https://www.pandadoc.com/blog/docusign-pricing/
- [경쟁사] https://signeasy.com/blog/business/docusign-pricing
- [경쟁사] https://signaturely.com/docusign-pricing/
