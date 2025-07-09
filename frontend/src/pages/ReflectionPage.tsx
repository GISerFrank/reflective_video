// src/pages/ReflectionPage.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import {
    Card,
    Input,
    Button,
    Space,
    Alert,
    Progress,
    Tag,
    Modal,
    message,
    Divider
} from 'antd';
import {
    EditOutlined,
    CheckCircleOutlined,
    ExclamationCircleOutlined,
    SaveOutlined,
    EyeOutlined
} from '@ant-design/icons';
import { useVideoStore, useReflectionStore } from '../store';
import { useRouteNavigation } from '../hooks/useRouteNavigation';
// @ts-ignore
import { Loading, ErrorMessage, PageHeader } from '../components/ui';
// @ts-ignore
import { debounce } from 'lodash';

const { TextArea } = Input;

const ReflectionPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const { currentVideo, fetchVideoWithProgress } = useVideoStore();
    const {
        isSubmitting,
        previewResult,
        error,
        createReflection,
        previewReflection,
        clearPreview,
        clearError
    } = useReflectionStore();
    const { goToVideoDetail, goBack } = useRouteNavigation();

    const [content, setContent] = useState('');
    const [showPreview, setShowPreview] = useState(false);
    const [wordCount, setWordCount] = useState(0);

    // 假设用户ID为1，实际应该从用户状态获取
    const userId = 1;

    useEffect(() => {
        if (id) {
            fetchVideoWithProgress(parseInt(id), userId);
        }
    }, [id, fetchVideoWithProgress]);

    // 防抖的预览函数
    const debouncedPreview = useCallback(
        debounce((text: string, videoId: number) => {
            if (text.length >= 50) {
                previewReflection(text, videoId);
            } else {
                clearPreview();
            }
        }, 1000),
        [previewReflection, clearPreview]
    );

    // 处理内容变化
    const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const value = e.target.value;
        setContent(value);
        setWordCount(value.length);

        if (id) {
            debouncedPreview(value, parseInt(id));
        }
    };

    // 提交观后感
    const handleSubmit = async () => {
        if (!id) return;

        if (content.length < 50) {
            message.warning('观后感内容至少需要50个字符');
            return;
        }

        const success = await createReflection(content, parseInt(id));
        if (success) {
            message.success('观后感提交成功！');
            goToVideoDetail(parseInt(id));
        }
    };

    // 显示预览模态框
    const handleShowPreview = () => {
        if (content.length < 50) {
            message.warning('观后感内容至少需要50个字符才能预览');
            return;
        }
        setShowPreview(true);
    };

    if (!currentVideo) {
        return <Loading tip="加载视频信息..." />;
    }

    const { video, progress } = currentVideo;

    // 检查是否有权限写观后感
    if (!progress || progress.completion_percentage < 50) {
        return (
            <div className="max-w-2xl mx-auto text-center py-12">
                <ExclamationCircleOutlined className="text-6xl text-orange-400 mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-4">无法写观后感</h2>
                <p className="text-gray-600 mb-6">
                    您需要观看视频至少50%才能写观后感。当前进度：{progress?.completion_percentage || 0}%
                </p>
                <Button type="primary" onClick={() => goToVideoDetail(video.id)}>
                    继续观看视频
                </Button>
            </div>
        );
    }

    const getQualityScoreColor = (score: number) => {
        if (score >= 80) return 'success';
        if (score >= 60) return 'warning';
        return 'error';
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <PageHeader
                title="写观后感"
                subtitle={`视频：${video.title}`}
                breadcrumbs={[
                    { title: '视频学习', path: '/videos' },
                    { title: video.title, path: `/videos/${video.id}` },
                    { title: '写观后感' }
                ]}
                onBack={goBack}
            />

            <ErrorMessage error={error} onClose={clearError} />

            <Card title="观后感编辑器">
                <div className="space-y-4">
                    {/* 写作指南 */}
                    <Alert
                        message="写作指南"
                        description={
                            <div className="space-y-2">
                                <p>• 观后感内容至少需要50个字符</p>
                                <p>• 建议包含具体的思考和感悟</p>
                                <p>• 可以提出问题或疑问</p>
                                <p>• 结合具体例子会获得更高质量分数</p>
                            </div>
                        }
                        type="info"
                        showIcon
                        className="mb-4"
                    />

                    {/* 编辑器 */}
                    <TextArea
                        value={content}
                        onChange={handleContentChange}
                        placeholder="请分享您观看这个视频后的思考和感悟..."
                        rows={12}
                        maxLength={2000}
                        showCount
                        className="text-base leading-relaxed"
                    />

                    {/* 实时反馈 */}
                    <div className="flex justify-between items-center text-sm text-gray-500">
                        <span>字数：{wordCount}</span>
                        <span>最少50字符，建议200字符以上</span>
                    </div>

                    {/* 质量预检测结果 */}
                    {previewResult && (
                        <Card size="small" className="bg-gray-50">
                            <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <span className="font-medium">质量预检测</span>
                                    {previewResult.valid ? (
                                        <Tag color="green" icon={<CheckCircleOutlined />}>
                                            可以提交
                                        </Tag>
                                    ) : (
                                        <Tag color="red" icon={<ExclamationCircleOutlined />}>
                                            需要改进
                                        </Tag>
                                    )}
                                </div>

                                {previewResult.quality_result && (
                                    <div>
                                        <div className="flex items-center justify-between mb-2">
                                            <span>质量分数</span>
                                            <span className="font-medium">
                        {previewResult.quality_result.quality_score}
                      </span>
                                        </div>
                                        <Progress
                                            percent={previewResult.quality_result.quality_score}
                                            status={getQualityScoreColor(previewResult.quality_result.quality_score)}
                                            strokeColor={{
                                                '0%': '#ff4d4f',
                                                '60%': '#faad14',
                                                '80%': '#52c41a',
                                            }}
                                        />
                                    </div>
                                )}

                                <div className="text-sm">
                  <span className="text-gray-600">
                    预计审核结果：
                  </span>
                                    <span className={`ml-2 font-medium ${
                                        previewResult.predicted_approval ? 'text-green-600' : 'text-orange-600'
                                    }`}>
                    {previewResult.predicted_approval ? '通过' : '需要改进'}
                  </span>
                                </div>

                                {previewResult.error && (
                                    <Alert
                                        message={previewResult.error}
                                        type="error"
                                        size="small"
                                    />
                                )}
                            </div>
                        </Card>
                    )}

                    {/* 操作按钮 */}
                    <div className="flex justify-between">
                        <Space>
                            <Button onClick={goBack}>
                                取消
                            </Button>
                            <Button
                                icon={<EyeOutlined />}
                                onClick={handleShowPreview}
                                disabled={content.length < 50}
                            >
                                预览
                            </Button>
                        </Space>

                        <Button
                            type="primary"
                            icon={<SaveOutlined />}
                            loading={isSubmitting}
                            onClick={handleSubmit}
                            disabled={content.length < 50}
                        >
                            提交观后感
                        </Button>
                    </div>
                </div>
            </Card>

            {/* 预览模态框 */}
            <Modal
                title="观后感预览"
                open={showPreview}
                onCancel={() => setShowPreview(false)}
                footer={[
                    <Button key="cancel" onClick={() => setShowPreview(false)}>
                        继续编辑
                    </Button>,
                    <Button
                        key="submit"
                        type="primary"
                        loading={isSubmitting}
                        onClick={handleSubmit}
                    >
                        确认提交
                    </Button>
                ]}
                width={700}
            >
                <div className="space-y-4">
                    <div>
                        <h4 className="font-medium mb-2">视频：{video.title}</h4>
                        <div className="text-sm text-gray-500">
                            字数：{wordCount} |
                            {previewResult?.quality_result &&
                                ` 质量分数：${previewResult.quality_result.quality_score}`
                            }
                        </div>
                    </div>

                    <Divider />

                    <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
                    </div>

                    {previewResult && previewResult.quality_result && (
                        <div className="text-sm text-gray-600">
                            <p>
                                预计审核结果：
                                <span className={`ml-1 font-medium ${
                                    previewResult.predicted_approval ? 'text-green-600' : 'text-orange-600'
                                }`}>
                  {previewResult.predicted_approval ? '通过审核' : '需要改进'}
                </span>
                            </p>
                        </div>
                    )}
                </div>
            </Modal>
        </div>
    );
};

export default ReflectionPage;