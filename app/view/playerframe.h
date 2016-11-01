/**
 * Copyright (C) 2016 Deepin Technology Co., Ltd.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 **/

#ifndef PLAYERFRAME_H
#define PLAYERFRAME_H

#include <DWindow>
#include <QScopedPointer>

DWIDGET_USE_NAMESPACE

class Playlist;
class MusicMeta;
class AppPresenter;
class MusicListWidget;
class PlayerFramePrivate;
class PlayerFrame : public DWindow
{
    Q_OBJECT

    Q_PROPERTY(QColor titlebarTopColor READ titlebarTopColor WRITE setTitlebarColor NOTIFY titlebarColorChanged)
    Q_PROPERTY(QColor titlebarBottomColor READ titlebarBottomColor WRITE setTitlebarBottomColor NOTIFY titlebarBottomColorChanged)
public:
    explicit PlayerFrame(QWidget *parent = 0);
    ~PlayerFrame();

    void initMusiclist(QSharedPointer<Playlist> allmusic, QSharedPointer<Playlist> last);
    void initPlaylist(QList<QSharedPointer<Playlist> > playlists, QSharedPointer<Playlist> last);
    void initFooter(QSharedPointer<Playlist> current, int mode);
    void binding(AppPresenter *presenter);

    void resizeEvent(QResizeEvent *e) Q_DECL_OVERRIDE;
    void paintEvent(QPaintEvent *e) Q_DECL_OVERRIDE;

    QColor titlebarTopColor() const
    {
        return m_titlebarTopColor;
    }

    QColor titlebarBottomColor() const
    {
        return m_titlebarBottomColor;
    }

signals:
    void importSelectFiles(const QStringList &filelist);
    void titlebarColorChanged(QColor titlebarTopColor);

    void titlebarBottomColorChanged(QColor titlebarBottomColor);

public slots:
    void onSelectImportFiles();

    void setTitlebarColor(QColor titlebarColor)
    {
        if (m_titlebarTopColor == titlebarColor) {
            return;
        }

        m_titlebarTopColor = titlebarColor;
        emit titlebarColorChanged(titlebarColor);
    }

    void setTitlebarBottomColor(QColor titlebarBottomColor)
    {
        if (m_titlebarBottomColor == titlebarBottomColor)
            return;

        m_titlebarBottomColor = titlebarBottomColor;
        emit titlebarBottomColorChanged(titlebarBottomColor);
    }

private:
    void initMenu();

    // disable control
    void disableControl();

    QScopedPointer<PlayerFramePrivate> d;
    QColor m_titlebarTopColor;
    QColor m_titlebarBottomColor;
};

#endif // PLAYERFRAME_H
