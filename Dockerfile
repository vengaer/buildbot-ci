FROM archlinux:latest
LABEL maintainer="vilhelm.engstrom@tuta.io"

COPY . /buildbot-ci
WORKDIR /buildbot-ci

RUN useradd -m builder                              && \
    pacman -Syu --noconfirm --needed python-pylint     \
                                     mypy              \
                                     python-black   && \
    chown -R builder:builder /buildbot-ci

USER builder
