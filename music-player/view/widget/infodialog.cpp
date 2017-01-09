/**
 * Copyright (C) 2016 Deepin Technology Co., Ltd.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 **/

#include "infodialog.h"

#include <QLabel>
#include <QVBoxLayout>
#include <QGridLayout>
#include <QPushButton>

#include <dwindowclosebutton.h>
#include <QDebug>
#include <thememanager.h>
#include "../../core/music.h"

InfoDialog::InfoDialog(const MusicMeta &info, QWidget *parent) : DAbstractDialog(parent)
{
    setObjectName("InfoDialog");
    setFixedWidth(320);

    auto layout = new QVBoxLayout(this);
    layout->setSpacing(0);
    layout->setMargin(5);

    auto closeBt = new DWindowCloseButton;
    closeBt->setObjectName("InfoClose");
    closeBt->setFixedSize(27, 23);
    closeBt->setAttribute(Qt::WA_NoMousePropagation);

    m_cover = new QLabel;
    m_cover->setContentsMargins(0, 0, 0, 0);
    m_cover->setObjectName("InfoCover");
    m_cover->setFixedSize(140, 140);

    auto title = new QLabel(info.title);
    title->setObjectName("InfoTitle");
    title->setFixedWidth(300);
    title->setWordWrap(true);

    auto split = new QLabel();
    split->setObjectName("InfoSplit");
    split->setFixedSize(300, 1);

    QStringList infoKeys;
    infoKeys << tr("Title:") << tr("Artist:") << tr("Album:")
             << tr("File type:") << tr("Size:") << tr("Length:")
             << tr("Directory:");

    QString artist = info.artist.isEmpty() ? tr("Unkonw Artist") : info.artist;
    QString album = info.album.isEmpty() ? tr("Unkonw Album") : info.album;
    QStringList infoValues;
    infoValues << info.title << artist << album
               << info.filetype << sizeString(info.size) << lengthString(info.length)
               << info.localPath;

    m_infogridFrame = new QFrame;
    m_infogridFrame->setMaximumWidth(300);
    m_infogridFrame->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
    auto infogridLayout = new QGridLayout(m_infogridFrame);
    infogridLayout->setMargin(0);
    infogridLayout->setHorizontalSpacing(5);
    infogridLayout->setVerticalSpacing(6);
    infogridLayout->setColumnStretch(0, 10);
    infogridLayout->setColumnStretch(1, 100);

    for (int i = 0; i < infoKeys.length(); ++i) {
        auto infoKey = new QLabel(infoKeys.value(i));
        infoKey->setObjectName("InfoKey");
        infoKey->setMinimumHeight(18);

        auto infoValue = new QLabel(infoValues.value(i));
        infoValue->setWordWrap(true);
        infoValue->setObjectName("InfoValue");
        infoValue->setMinimumHeight(18);
//        infoValue->setMaximumWidth(250);
        infoValue->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
        m_valueList << infoValue;

        infogridLayout->addWidget(infoKey);
        infogridLayout->addWidget(infoValue);
    }

    layout->addWidget(closeBt, 0, Qt::AlignTop | Qt::AlignRight);
    layout->addSpacing(43);
    layout->addWidget(m_cover, 0, Qt::AlignCenter);
    layout->addSpacing(13);
    layout->addWidget(title, 0, Qt::AlignCenter);
    layout->addSpacing(19);
    layout->addWidget(split, 0, Qt::AlignCenter);
    layout->addSpacing(10);
    layout->addWidget(m_infogridFrame, 0, Qt::AlignCenter);
    layout->addSpacing(10);
    layout->addStretch();

    ThemeManager::instance()->regisetrWidget(this);


    connect(closeBt, &DWindowCloseButton::clicked, this, &DAbstractDialog::close);
}

void InfoDialog::updateLabelSize()
{
    m_infogridFrame->adjustSize();
    for (auto label : m_valueList) {
        label->adjustSize();
    }
    adjustSize();
}

QString InfoDialog::defaultCover() const
{
    return this->property("DefaultCover").toString();
}

void InfoDialog::setDefaultCover(QString defaultCover)
{
    this->setProperty("DefaultCover", defaultCover);
}

void InfoDialog::setCoverImage(const QPixmap &coverPixmap)
{
    if (!coverPixmap.isNull()) {
        m_cover->setPixmap(coverPixmap.scaled(140, 140));
    } else {
        m_cover->setPixmap(QPixmap(defaultCover()).scaled(140, 140));
    }
}