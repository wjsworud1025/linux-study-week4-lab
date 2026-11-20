# 4주차 교차 검증 · 방문 기록이 남는 웹 서비스

**공용 리허설** — 이 저장소에서 소개 페이지에 방문 기록을 한 건 쓰고, DB 컨테이너를 교체한 뒤 같은 번호를 읽습니다. 아래 명령은 같은 Bash 터미널에서 순서대로 실행하세요. 이미지 다운로드를 포함해 약 15~30분 걸립니다.

**최종 교차 검증** — 서로 앱 저장소 URL과 검증할 커밋 SHA를 교환합니다. 검증자는 짝의 저장소를 복제한 뒤 `git switch --detach 전달받은_SHA`로 전환하고 `git rev-parse HEAD`로 SHA를 확인합니다. 이후 **그 커밋의 README만** 따라 실행합니다. 아래 공용 절차는 각자 README를 작성할 때 참고하세요. 결과 제출에는 대상 URL·커밋, 실행 환경, 독립 실행 여부와 관찰값이 필요합니다.

## 1. 준비와 복제

Git, curl, OpenSSL, Docker Engine과 Compose v2가 필요합니다. `docker version`에 Server가 나오고 `docker compose version`이 성공하는지 확인하세요. VM에서 Docker 실행에 관리자 권한이 필요하면 아래 Docker 명령에 `sudo`를 붙입니다. VM 터미널에서 `ss -ltn 'sport = :8080'`을 실행해 8080에 대기 중인 서비스가 없는지 봅니다. 포트가 사용 중이면 해당 실습 서비스를 종료하거나 새 VM을 사용합니다.

```bash
lab_dir="week4-lab-$(openssl rand -hex 6)"
git clone https://github.com/wjsworud1025/linux-study-week4-lab.git "$lab_dir"
cd "$lab_dir"
git rev-parse HEAD
```

공용 랩에서 Compose 프로젝트 이름을 따로 지정하지 않았다면 복제 폴더의 임의 이름으로 프로젝트와 DB 볼륨이 구분됩니다. 짝의 저장소를 검증할 때는 README 지침에 따라 회차별 고유 이름을 `-p 이름`으로 지정하고, 종료·재기동까지 모든 Compose 명령에 같은 이름을 사용합니다.

## 2. 로컬 암호를 준비하고 시작하기

처음 복제한 폴더에서 실행합니다. 암호는 이 VM의 .env 파일에 보관하며 같은 볼륨을 쓸 동안 유지합니다. config 검사가 성공하면 출력이 없습니다.

```bash
test -f .env || (umask 077; printf 'DB_PASSWORD=%s\n' "$(openssl rand -hex 24)" > .env)
docker compose config --quiet
docker compose up -d --build --wait
docker compose ps
```

목록에서 db는 healthy, web은 실행 상태여야 합니다. 실패하면 `docker compose logs --tail 30 db web`에서 먼저 종료된 서비스의 오류를 확인하세요.

## 3. 소개 페이지에 한 번 방문하기

아래 요청은 DB에 행 하나를 추가합니다. 페이지의 ‘우리 리눅스 스터디’와 `Visit #숫자`를 확인하세요. 방문 번호를 응답에서 직접 저장하므로 여러 번 실습해도 번호가 1일 필요가 없습니다.

```bash
base=http://127.0.0.1:8080
page=$(curl -fsS --retry 5 --retry-connrefused "$base/")
printf '%s\n' "$page"
visit=$(printf '%s\n' "$page" | sed -n 's/.*Visit #\([0-9][0-9]*\).*/\1/p')
db_before=$(docker compose ps -q db)
printf '방문 번호: %s\nDB 교체 전: %.12s\n' "$visit" "$db_before"
docker compose logs --tail 20 web | grep 'GET / HTTP'
```

방문 번호와 DB ID가 모두 표시되고 웹 로그에 200이 찍혔는지 확인하세요. 최종 교차 검증에서는 짝의 README로 확인한 값을 결과 이슈에 기록합니다.

## 4. 새 DB 컨테이너에서 기존 번호 조회하기

`down`은 이 프로젝트의 컨테이너를 정리하고 이름 있는 볼륨은 남깁니다. 이 단계에서 `-v`를 붙이면 보존을 확인할 볼륨까지 지워집니다. 같은 폴더, 같은 터미널에서 이어서 실행하세요.

```bash
docker compose down
docker compose up -d --wait
db_after=$(docker compose ps -q db)
printf 'DB 교체 후: %.12s\n' "$db_after"
visits=$(curl -fsS --retry 5 --retry-connrefused "$base/visits")
if test -n "$visit" && test -n "$db_before" && test -n "$db_after" && test "$db_before" != "$db_after" && printf '%s\n' "$visits" | grep -Fx "$visit"; then
  echo '검증 성공: 새 DB 컨테이너에서 기존 방문 번호 확인'
else
  echo '검증 실패: 두 DB ID와 방문 번호 목록 확인'
  false
fi
```

`/visits`는 기록을 추가하지 않는 조회 경로입니다. 두 ID가 다르고, 저장해 둔 번호가 조회 결과에 한 줄로 나오면 통과입니다.

## 5. 종료하고 최종 검증 결과 공유하기

```bash
docker compose down
```

짝의 저장소를 검증했으면 [교차 검증 결과 이슈 작성](https://github.com/wjsworud1025/linux-study-week4-lab/issues/new?template=cross-check.yml)을 엽니다. 검증한 URL·커밋, 환경, README만 사용했는지와 관찰값을 기록합니다. 막혔다면 마지막 성공 단계와 오류를 기록합니다. 결과 이슈 주소를 개인 실습 글에 첨부합니다. [4주차 가이드](https://wjsworud1025.github.io/linux-study/guides/week-4/)
