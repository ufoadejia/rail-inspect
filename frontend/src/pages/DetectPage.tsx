import { useState } from 'react'
import { Upload, Button, Select, Descriptions, Tag, Typography, message, Row, Col, Card, Empty, Space } from 'antd'
import { UploadOutlined, ScanOutlined, CheckCircleTwoTone, WarningTwoTone, CloseCircleTwoTone } from '@ant-design/icons'
import { detectDefect } from '../api'

const { Paragraph, Text } = Typography

const gradeMeta: Record<string, { color: string; bg: string; icon: any }> = {
  '正常': { color: '#16a34a', bg: '#e8f7ee', icon: CheckCircleTwoTone },
  '轻伤': { color: '#f59e0b', bg: '#fef4e2', icon: WarningTwoTone },
  '重伤': { color: '#ef4444', bg: '#fdeaea', icon: CloseCircleTwoTone },
  '待判定': { color: '#6b7280', bg: '#f3f4f6', icon: WarningTwoTone },
}

export default function DetectPage() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string>('')
  const [imageType, setImageType] = useState('surface')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const onFile = (f: File | undefined) => {
    if (!f) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setResult(null)
    return false
  }

  const handleDetect = async () => {
    if (!file) { message.warning('请先上传探伤图片'); return }
    setLoading(true)
    try {
      const data = await detectDefect(file, imageType)
      setResult(data)
    } catch (e: any) {
      message.error('识别失败：' + (e.message || '请检查后端服务'))
    } finally {
      setLoading(false)
    }
  }

  const gm = result ? gradeMeta[result.defect_grade] || gradeMeta['待判定'] : null
  const GradeIcon = gm?.icon

  return (
    <div>
      <div className="page-header">
        <h2>缺陷识别</h2>
        <div className="sub">上传钢轨表面照片或超声波 A / B / C 扫图，多模态大模型自动识别缺陷类型并判级</div>
      </div>

      <Row gutter={20}>
        <Col span={11}>
          <Card className="platform-card" title="上传探伤图像">
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <div className="flex" style={{ alignItems: 'center', gap: 8 }}>
                <Text type="secondary">图像类型：</Text>
                <Select value={imageType} onChange={setImageType} style={{ width: 220 }}
                  options={[
                    { value: 'surface', label: '表面照片' },
                    { value: 'a_scan', label: 'A 型显示（超声波形）' },
                    { value: 'b_scan', label: 'B 扫成像' },
                    { value: 'c_scan', label: 'C 扫成像' },
                  ]} />
              </div>

              <Upload.Dragger
                accept="image/*"
                maxCount={1}
                showUploadList={false}
                beforeUpload={onFile}
                style={{ padding: '16px 8px' }}
              >
                {preview ? (
                  <img src={preview} alt="预览" style={{ maxHeight: 200, maxWidth: '100%', borderRadius: 4 }} />
                ) : (
                  <>
                    <p className="ant-upload-drag-icon"><UploadOutlined style={{ color: '#2f6bff', fontSize: 36 }} /></p>
                    <p className="ant-upload-text">点击或拖拽上传探伤图片</p>
                    <p className="ant-upload-hint">支持 JPG / PNG，单张上传</p>
                  </>
                )}
              </Upload.Dragger>

              <Button type="primary" icon={<ScanOutlined />} loading={loading}
                onClick={handleDetect} block size="large">
                开始识别
              </Button>
            </Space>
          </Card>
        </Col>

        <Col span={13}>
          <Card className="platform-card" title="识别结果">
            {result && gm && GradeIcon ? (
              <>
                <div style={{
                  background: gm.bg, borderRadius: 8, padding: '16px 20px',
                  display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16,
                  border: `1px solid ${gm.color}33`,
                }}>
                  <GradeIcon twoToneColor={gm.color} style={{ fontSize: 38 }} />
                  <div>
                    <div style={{ fontSize: 13, color: '#6b7280' }}>判定结果</div>
                    <div style={{ fontSize: 24, fontWeight: 700, color: gm.color, lineHeight: 1.2 }}>
                      {result.defect_grade}
                    </div>
                  </div>
                  <Tag color="blue" style={{ marginLeft: 'auto', fontSize: 14, padding: '4px 12px' }}>
                    {result.defect_type_cn}
                  </Tag>
                </div>

                <Descriptions column={2} bordered size="small" labelStyle={{ width: 100, background: '#f7f9fc' }}>
                  <Descriptions.Item label="缺陷类型" span={2}>{result.defect_type_cn}</Descriptions.Item>
                  <Descriptions.Item label="判级">{result.defect_grade}</Descriptions.Item>
                  <Descriptions.Item label="回波当量">{result.db_value != null ? `${result.db_value} dB` : '—'}</Descriptions.Item>
                  <Descriptions.Item label="置信度">{((result.confidence || 0) * 100).toFixed(1)}%</Descriptions.Item>
                  <Descriptions.Item label="图像类型">{imageType}</Descriptions.Item>
                  <Descriptions.Item label="描述" span={2}>{result.description}</Descriptions.Item>
                </Descriptions>
              </>
            ) : (
              <Empty description="上传图片并点击「开始识别」查看结果" style={{ padding: '60px 0' }} />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}
